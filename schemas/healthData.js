const mongoose = require('mongoose')

const profileSchema = new mongoose.Schema({
  nickname: String,
  age_range: {
    type: String,
    enum: ['18-20', '20-25', '25-30', '30-35', '35-40', '40-45', '45-50', '50+']
  },
  ethnicity: String,
  location: String,
  is_pregnant: Boolean
})

const diseaseStateSchema = new mongoose.Schema({
  condition_name: { type: String, required: true },
  is_self_diagnosed: Boolean,
  diagnosis_method: {
    type: String,
    enum: ['Doctor', 'Research', 'Other']
  },
  treatments: String,
  subtype: String,
  first_symptom_date: String,
  wants_future_studies: Boolean
})



const medicationSchema = new mongoose.Schema({
  med_name: { type: String, required: true },
  verified: { type: Boolean, default: false },
  related_condition: String
})

const healthDataSchema = new mongoose.Schema({
  user_hash: { type: String, required: true },
  healthDataId: { type: String, required: true, unique: true },
  research_opt_in: { type: Boolean, default: false },
  profile: profileSchema,
  disease_states: [diseaseStateSchema],
  medications: [medicationSchema],
  timestamp: { type: Date, default: Date.now }
})

module.exports = mongoose.model('HealthData', healthDataSchema)



// const healthDataSchema = {
//   "user_hash": "hashed_uuid",
//   "healthDataId": "uuid",
//   "research_opt_in": true,
//   "profile": {
//       "nickname": "string",
//       "age_range": "20-25", // Changed to match form's age range format
//       "ethnicity": "string",
//       "location": "string (country/state only)",
//       "is_pregnant": false
//   },
//   "disease_states": [
//       {  
//           "condition_name": "string",
//           "is_self_diagnosed": true,
//           "diagnosis_method": "string (Doctor/Research/Other)",
//           "treatments": "string (e.g. CBT)",
//           "subtype": "string",
//           "first_symptom_date": "string (age range when started)",
//           "wants_future_studies": false
//       }
//   ],
//   "medications": [
//       {
//           "med_name": "string (from OpenPIL/Open FDA)",
//           "verified": true,
//           "related_condition": "string" // Link to condition it treats
//       }
//   ],
//   "timestamp": "ISO 8601 datetime"
// }