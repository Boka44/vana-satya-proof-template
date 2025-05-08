
const profileSchema = new mongoose.Schema({
  age_range: {
    type: String,
    enum: ['18-20', '20-25', '25-30', '30-35', '35-40', '40-45', '45-50', '50+']
  },
  ethnicity: String,
  location: String,
  is_pregnant: Boolean
})


const healthDataSchema = new mongoose.Schema({
  healthDataId: { type: String, required: true },
  user_hash: { type: String, required: true },
  research_opt_in: { type: Boolean, default: false },
  profile: profileSchema,
  conditions: { type: [String] },
  medications: { type: [String] },
  treatments: { type: [String] },
  caretaker: { type: [String] },
  timestamp: { type: Date, default: Date.now }
})