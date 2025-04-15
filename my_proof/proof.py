import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

import requests

from my_proof.models.proof_response import ProofResponse


class Proof:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.proof_response = ProofResponse(dlp_id=config['dlp_id'])

    def generate(self) -> ProofResponse:
        """Generate proofs for either health profile or daily check-in."""
        logging.info("Starting proof generation")

        # Load the input file
        input_files = os.listdir(self.config['input_dir'])
        if not input_files:
            logging.error("No input file found")
            self.proof_response.valid = False
            return self.proof_response

        # Debug: Print what files we see
        logging.info(f"Found input files: {input_files}")

        for input_filename in input_files:
            input_file = os.path.join(self.config['input_dir'], input_filename)
            if not input_file.lower().endswith('.json'):
                continue

            with open(input_file, 'r') as f:
                data = json.load(f)
                logging.info(f"Processing file {input_filename}")

                # Check for health profile
                if 'healthDataId' in data:
                    return self._process_health_profile(data)
                # Check for check-in
                elif 'mood' in data:
                    return self._process_daily_checkin(data)

        logging.error("No valid health profile or check-in data found")
        self.proof_response.valid = False
        return self.proof_response

    def _process_health_profile(self, health_data: Dict) -> ProofResponse:
        """Process health profile data."""
        # Calculate quality based on profile completeness
        quality_score = self._calculate_profile_quality(health_data)
        
        # Calculate ownership score
        ownership_score = self._verify_health_profile_ownership(health_data)
        
        # Set proof scores
        self.proof_response.quality = quality_score
        self.proof_response.ownership = ownership_score
        self.proof_response.authenticity = 1.0  # Base authenticity for profile
        self.proof_response.uniqueness = self._calculate_profile_uniqueness(health_data)

        # Calculate overall score
        self.proof_response.score = (
            0.4 * self.proof_response.quality +
            0.4 * self.proof_response.ownership +
            0.2 * self.proof_response.uniqueness
        )

        # Determine validity
        self.proof_response.valid = (
            self.proof_response.ownership >= 0.8 and  # Must have strong ownership proof
            self.proof_response.quality >= 0.5        # Minimum quality threshold
        )

        # Add metadata
        self.proof_response.attributes = {
            'data_type': 'health_profile',
            'profile_completeness': quality_score,
            'has_disease_states': len(health_data.get('disease_states', [])) > 0,
            'has_medications': len(health_data.get('medications', [])) > 0,
            'research_opted_in': health_data.get('research_opt_in', False)
        }

        return self.proof_response

    def _process_daily_checkin(self, checkin_data: Dict) -> ProofResponse:
        """Process daily check-in data."""
        # Calculate quality based on check-in completeness
        quality_score = self._calculate_checkin_quality(checkin_data)
        
        # Calculate ownership score
        ownership_score = self._verify_checkin_ownership(checkin_data)

        # Set proof scores
        self.proof_response.quality = quality_score
        self.proof_response.ownership = ownership_score
        self.proof_response.authenticity = self._calculate_checkin_authenticity(checkin_data)
        self.proof_response.uniqueness = 1.0  # Each check-in is unique by timestamp

        # Calculate overall score
        self.proof_response.score = (
            0.5 * self.proof_response.quality +
            0.3 * self.proof_response.ownership +
            0.2 * self.proof_response.authenticity
        )

        # Determine validity
        self.proof_response.valid = (
            self.proof_response.ownership >= 0.8 and  # Must have strong ownership proof
            self.proof_response.quality >= 0.5        # Minimum quality threshold
        )

        # Add metadata
        self.proof_response.attributes = {
            'data_type': 'daily_checkin',
            'checkin_completeness': quality_score,
            'has_health_comment': bool(checkin_data.get('health_comment')),
            'has_updates': any([
                checkin_data.get('doctor_visit'),
                checkin_data.get('medication_update'),
                checkin_data.get('diagnosis_update')
            ])
        }

        return self.proof_response

    def _calculate_profile_quality(self, health_data: Dict) -> float:
        """Calculate quality score for health profile."""
        required_fields = {'nickname', 'age_range', 'ethnicity', 'location'}
        profile = health_data.get('profile', {})
        
        # Basic profile completeness
        filled_fields = sum(1 for field in required_fields if profile.get(field))
        score = filled_fields / len(required_fields)

        # Bonus for additional data
        if health_data.get('disease_states'):
            score += 0.2
        if health_data.get('medications'):
            score += 0.2

        return min(1.0, score)

    def _calculate_checkin_quality(self, checkin: Dict) -> float:
        """Calculate quality score for daily check-in."""
        required_fields = {
            'mood', 'health_comment', 'doctor_visit',
            'medication_update', 'diagnosis_update'
        }
        
        # Calculate completeness
        filled_fields = sum(1 for field in required_fields if checkin.get(field) is not None)
        score = filled_fields / len(required_fields)

        # Bonus for detailed health comment
        if checkin.get('health_comment', '').strip():
            score += 0.2

        return min(1.0, score)

    def _verify_health_profile_ownership(self, health_data: Dict) -> float:
        """Verify ownership of health profile."""
        score = 0.0
        
        if not health_data.get('user_hash'):
            return score
        
        score += 0.4  # Base score for having user_hash

        # Additional verification factors
        if health_data.get('healthDataId'):
            score += 0.2
        
        profile = health_data.get('profile', {})
        if all(profile.get(field) for field in ['nickname', 'age_range', 'location']):
            score += 0.2
        
        if health_data.get('research_opt_in') is not None:
            score += 0.2
            
        return min(1.0, score)

    def _verify_checkin_ownership(self, checkin: Dict) -> float:
        """Verify ownership of daily check-in."""
        score = 0.0
        
        if not checkin.get('user_hash'):
            return score
        
        score += 0.6  # Base score for having user_hash

        # Additional verification factors
        if checkin.get('timestamp'):
            score += 0.2
        
        if checkin.get('mood'):
            score += 0.2
            
        return min(1.0, score)

    def _calculate_checkin_authenticity(self, checkin: Dict) -> float:
        """Calculate authenticity score for check-in."""
        score = 1.0

        try:
            # Convert timestamp to UTC datetime
            check_time = datetime.fromisoformat(checkin.get('timestamp').replace('Z', '+00:00'))
            # Make sure 'now' is also UTC
            now = datetime.now().astimezone()
            
            if check_time > now:
                score *= 0.5  # Future timestamp
            elif (now - check_time).days > 7:
                score *= 0.8  # Old check-in
                
        except (ValueError, AttributeError):
            score *= 0.7  # Invalid timestamp

        return score

    def _calculate_profile_uniqueness(self, health_data: Dict) -> float:
        """Calculate uniqueness score for health profile."""
        score = 0.5  # Base uniqueness score
        
        # Bonus for specific conditions and medications
        if health_data.get('disease_states'):
            score += 0.25
        if health_data.get('medications'):
            score += 0.25
            
        return score


def fetch_random_number() -> float:
    """Demonstrate HTTP requests by fetching a random number from random.org."""
    try:
        response = requests.get('https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new')
        return float(response.text.strip())
    except requests.RequestException as e:
        logging.warning(f"Error fetching random number: {e}. Using local random.")
        return __import__('random').random()
