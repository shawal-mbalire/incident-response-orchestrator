output "database_name" {
  description = "Name of the Firestore database"
  value       = google_firestore_database.default.name
}
