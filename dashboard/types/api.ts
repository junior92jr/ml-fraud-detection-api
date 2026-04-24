export interface Transaction {
  id: number
  transaction_id: string
  amount: number
  transaction_hour: number
  merchant_category: string
  foreign_transaction: boolean
  location_mismatch: boolean
  device_trust_score: number
  velocity_last_24h: number
  cardholder_age: number
}

export interface FraudPrediction {
  id: number
  transaction_id: string
  fraud_probability: number
  decision: number | string // 0 = Approve, 1 = Reject
  scored_at: string
}

export interface ScoreTransactionRequest {
  transaction_id: string
  amount: number
  transaction_hour: number
  merchant_category: string
  foreign_transaction: boolean
  location_mismatch: boolean
  device_trust_score: number
  velocity_last_24h: number
  cardholder_age: number
}

export interface TransactionUpdateRequest {
  amount?: number
  transaction_hour?: number
  merchant_category?: string
  foreign_transaction?: boolean
  location_mismatch?: boolean
  device_trust_score?: number
  velocity_last_24h?: number
  cardholder_age?: number
}

export interface ScoreTransactionResponse {
  transaction_id: string
  fraud_probability: number
  decision: number
  threshold: number
  scored_at: string
}

export interface TransactionDetailsResponse {
  transaction: Transaction
  predictions: FraudPrediction[]
}

export interface TransactionImportError {
  line: number
  transaction_id?: string
  error: string
}

export interface TransactionImportResponse {
  total_rows: number
  imported: number
  skipped_duplicates: number
  skipped_invalid: number
  skipped_scoring_errors: number
  errors: TransactionImportError[]
}
