const mongoose = require('mongoose')

const checkInSchema = new mongoose.Schema({
  user_hash: { type: String, required: true },
  is_pregnant: Boolean,
  timestamp: { type: Date, default: Date.now },
  mood: String,
  health_comment: String,
  doctor_visit: Boolean,
  medication_update: Boolean,
  diagnosis_update: Boolean
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