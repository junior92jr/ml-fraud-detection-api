"use client"

import { useState } from "react"
import { useForm, Controller } from "react-hook-form"
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormControlLabel,
  Checkbox,
  Box,
  Alert,
  CircularProgress,
  Chip,
  FormHelperText,
} from "@mui/material"
import { Send } from "@mui/icons-material"
import Navigation from "./Navigation"
import type { ScoreTransactionRequest, ScoreTransactionResponse } from "@/types/api"
import { scoreTransaction } from "@/lib/api"

export default function ScoreTransactionForm() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ScoreTransactionResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<ScoreTransactionRequest>({
    defaultValues: {
      transaction_id: "",
      amount: 0,
      transaction_hour: 12,
      merchant_category: "Electronics",
      foreign_transaction: false,
      location_mismatch: false,
      device_trust_score: 50,
      velocity_last_24h: 0,
      cardholder_age: 30,
    },
  })

  const onSubmit = async (data: ScoreTransactionRequest) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response: ScoreTransactionResponse = await scoreTransaction(data)
      setResult(response)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to score transaction. Please try again."
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const getFraudColor = (probability: number) => {
    if (probability < 0.3) return "success"
    if (probability < 0.7) return "warning"
    return "error"
  }

  return (
    <>
      <Navigation />
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Score Transaction
        </Typography>

        <Paper sx={{ p: 4 }}>
          <form onSubmit={handleSubmit(onSubmit)}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Controller
                  name="transaction_id"
                  control={control}
                  rules={{ required: "Transaction ID is required" }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Transaction ID"
                      fullWidth
                      error={!!errors.transaction_id}
                      helperText={errors.transaction_id?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="amount"
                  control={control}
                  rules={{
                    required: "Amount is required",
                    min: { value: 0.01, message: "Amount must be greater than 0" },
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Amount"
                      type="number"
                      fullWidth
                      inputProps={{ step: "0.01" }}
                      error={!!errors.amount}
                      helperText={errors.amount?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="transaction_hour"
                  control={control}
                  rules={{
                    required: "Transaction hour is required",
                    min: { value: 0, message: "Hour must be between 0-23" },
                    max: { value: 23, message: "Hour must be between 0-23" },
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Transaction Hour (0-23)"
                      type="number"
                      fullWidth
                      error={!!errors.transaction_hour}
                      helperText={errors.transaction_hour?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <Controller
                  name="merchant_category"
                  control={control}
                  rules={{ required: "Merchant category is required" }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.merchant_category}>
                      <InputLabel>Merchant Category</InputLabel>
                      <Select {...field} label="Merchant Category">
                        <MenuItem value="Electronics">Electronics</MenuItem>
                        <MenuItem value="Travel">Travel</MenuItem>
                        <MenuItem value="Grocery">Grocery</MenuItem>
                        <MenuItem value="Food">Food</MenuItem>
                        <MenuItem value="Clothing">Clothing</MenuItem>
                      </Select>
                      {errors.merchant_category && <FormHelperText>{errors.merchant_category.message}</FormHelperText>}
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="foreign_transaction"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Checkbox {...field} checked={field.value} />}
                      label="Foreign Transaction"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="location_mismatch"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Checkbox {...field} checked={field.value} />}
                      label="Location Mismatch"
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <Controller
                  name="device_trust_score"
                  control={control}
                  rules={{
                    required: "Device trust score is required",
                    min: { value: 0, message: "Score must be between 0-100" },
                    max: { value: 100, message: "Score must be between 0-100" },
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Device Trust Score (0-100)"
                      type="number"
                      fullWidth
                      error={!!errors.device_trust_score}
                      helperText={errors.device_trust_score?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <Controller
                  name="velocity_last_24h"
                  control={control}
                  rules={{
                    required: "Velocity is required",
                    min: { value: 0, message: "Velocity must be >= 0" },
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Velocity Last 24h"
                      type="number"
                      fullWidth
                      error={!!errors.velocity_last_24h}
                      helperText={errors.velocity_last_24h?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <Controller
                  name="cardholder_age"
                  control={control}
                  rules={{
                    required: "Cardholder age is required",
                    min: { value: 18, message: "Age must be between 18-100" },
                    max: { value: 100, message: "Age must be between 18-100" },
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Cardholder Age (18-100)"
                      type="number"
                      fullWidth
                      error={!!errors.cardholder_age}
                      helperText={errors.cardholder_age?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  fullWidth
                  startIcon={loading ? <CircularProgress size={20} /> : <Send />}
                  disabled={loading}
                >
                  {loading ? "Scoring..." : "Score Transaction"}
                </Button>
              </Grid>
            </Grid>
          </form>

          {error && (
            <Alert severity="error" sx={{ mt: 3 }}>
              {error}
            </Alert>
          )}

          {result && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom>
                Fraud Score Result
              </Typography>
              <Paper variant="outlined" sx={{ p: 3 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Fraud Probability
                    </Typography>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Typography variant="h4">{(result.fraud_probability * 100).toFixed(2)}%</Typography>
                      <Chip
                        label={getFraudColor(result.fraud_probability)}
                        color={getFraudColor(result.fraud_probability)}
                        size="small"
                      />
                    </Box>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Decision
                    </Typography>
                    <Chip
                      label={result.decision === 0 ? "Approve" : "Reject"}
                      color={result.decision === 0 ? "success" : "error"}
                      sx={{ mt: 1, fontSize: "1.2rem", p: 2 }}
                    />
                  </Grid>

                  <Grid item xs={12} sm={4}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Threshold
                    </Typography>
                    <Typography variant="h6">{result.threshold}</Typography>
                  </Grid>

                  <Grid item xs={12} sm={4}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Scored At
                    </Typography>
                    <Typography variant="body2">{new Date(result.scored_at).toLocaleString()}</Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Box>
          )}
        </Paper>
      </Container>
    </>
  )
}
