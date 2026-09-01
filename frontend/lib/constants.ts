/**
 * Fixed reference values mirroring backend/scripts/reference_data.py —
 * used for filter/form dropdowns. Payers and service types are plain
 * denormalized strings in the data model (not their own collection),
 * so the frontend keeps its own copy of the known set, same as the seed.
 */
export const PAYERS = ["Aetna", "UnitedHealthcare", "Cigna", "Molina Healthcare", "Anthem Blue Cross"];

export const SERVICE_TYPES = [
  "Behavioral Health",
  "Case Management",
  "Home Health Aide",
  "Nutrition Counseling",
  "Occupational Therapy",
  "Physical Therapy",
  "Skilled Nursing",
  "Speech Therapy",
];
