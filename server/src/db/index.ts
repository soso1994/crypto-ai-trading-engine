import { Pool } from "pg";

// Simple PG pool. Configure via DATABASE_URL env var.
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  // Optional: provide SSL settings in production
});

export default pool;
