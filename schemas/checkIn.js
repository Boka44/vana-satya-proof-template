const mongoose = require('mongoose')

const checkInSchema = new mongoose.Schema({
  user_hash: { type: String, required: true },
  timestamp: { type: Date, default: Date.now },
  mood: String,
  health_comment: String,
  doctor_visit: Boolean,
  health_profile_update: Boolean,
  anxiety_level: String,
  anxiety_details: String,
  pain_level: Number,
  pain_details: String,
  fatigue_level: Number,
  fatigue_details: String
})

module.exports = mongoose.model('CheckIn', checkInSchema)


// const checkInSchema = {
//   "user_hash": "hashed_uuid",
//   "is_pregnant": false,
//   "timestamp": "ISO 8601 datetime",
//   "mood": "good",
//   "health_comment": "Feeling fine today", // could be risky to allow free text
//   "doctor_visit": false,
//   "medication_update": false,
//   "diagnosis_update": false
// }