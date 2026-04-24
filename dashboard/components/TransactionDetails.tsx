"use client"

import { useState, useEffect } from "react"
import {
  Container,
  Paper,
  Typography,
  Grid,
  Box,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
} from "@mui/material"
import { ArrowBack, CheckCircle, Cancel } from "@mui/icons-material"
import { useRouter } from "next/navigation"
import Navigation from "./Navigation"
import type { Transaction, FraudPrediction, TransactionUpdateRequest } from "@/types/api"
import { getTransactionById, updateTransaction } from "@/lib/api"

interface TransactionDetailsProps {
  transactionId: string
}

export default function TransactionDetails({ transactionId }: TransactionDetailsProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [transaction, setTransaction] = useState<Transaction | null>(null)
  const [predictions, setPredictions] = useState<FraudPrediction[]>([])
  const [updateLoading, setUpdateLoading] = useState(false)
  const [updateMessage, setUpdateMessage] = useState<string | null>(null)
  const [updateForm, setUpdateForm] = useState<TransactionUpdateRequest>({
    amount: undefined,
    transaction_hour: undefined,
    merchant_category: undefined,
    foreign_transaction: undefined,
    location_mismatch: undefined,
    device_trust_score: undefined,
    velocity_last_24h: undefined,
    cardholder_age: undefined,
  })

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await getTransactionById(transactionId)
        setTransaction(data.transaction)
        setPredictions(data.predictions)
        setUpdateForm({
          amount: data.transaction.amount,
          transaction_hour: data.transaction.transaction_hour,
          merchant_category: data.transaction.merchant_category,
          foreign_transaction: data.transaction.foreign_transaction,
          location_mismatch: data.transaction.location_mismatch,
          device_trust_score: data.transaction.device_trust_score,
          velocity_last_24h: data.transaction.velocity_last_24h,
          cardholder_age: data.transaction.cardholder_age,
        })
      } catch (err) {
        const message = err instanceof Error ? err.message : "Transaction not found"
        setError(message)
      } finally {
        setLoading(false)
      }
    }

    void load()
  }, [transactionId])

  const getFraudColor = (probability: number) => {
    if (probability < 0.3) return "success"
    if (probability < 0.7) return "warning"
    return "error"
  }

  const decisionValue = (decision: number | string) => Number(decision)

  const refreshTransaction = async () => {
    const data = await getTransactionById(transactionId)
    setTransaction(data.transaction)
    setPredictions(data.predictions)
  }

  const handleUpdateAndRescore = async () => {
    if (!transaction) return
    setUpdateLoading(true)
    setUpdateMessage(null)

    try {
      await updateTransaction(transaction.transaction_id, updateForm)
      await refreshTransaction()
      setUpdateMessage("Transaction updated and rescored.")
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to update transaction."
      setUpdateMessage(message)
    } finally {
      setUpdateLoading(false)
    }
  }

  if (loading) {
    return (
      <>
        <Navigation />
        <Container sx={{ mt: 4, display: "flex", justifyContent: "center" }}>
          <CircularProgress />
        </Container>
      </>
    )
  }

  if (error || !transaction) {
    return (
      <>
        <Navigation />
        <Container sx={{ mt: 4 }}>
          <Alert severity="error">{error || "Transaction not found"}</Alert>
          <Button startIcon={<ArrowBack />} onClick={() => router.push("/transactions")} sx={{ mt: 2 }}>
            Back to Transactions
          </Button>
        </Container>
      </>
    )
  }

  return (
    <>
      <Navigation />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Button startIcon={<ArrowBack />} onClick={() => router.push("/transactions")} sx={{ mb: 2 }}>
          Back to Transactions
        </Button>

        <Typography variant="h4" gutterBottom>
          Transaction Details
        </Typography>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Transaction Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Transaction ID
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {transaction.transaction_id}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Amount
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                ${transaction.amount.toFixed(2)}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Merchant Category
              </Typography>
              <Typography variant="body1">{transaction.merchant_category}</Typography>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Transaction Hour
              </Typography>
              <Typography variant="body1">{transaction.transaction_hour}:00</Typography>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Foreign Transaction
              </Typography>
              {transaction.foreign_transaction ? (
                <Chip icon={<CheckCircle />} label="Yes" color="warning" size="small" />
              ) : (
                <Chip icon={<Cancel />} label="No" size="small" />
              )}
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Location Mismatch
              </Typography>
              {transaction.location_mismatch ? (
                <Chip icon={<CheckCircle />} label="Yes" color="warning" size="small" />
              ) : (
                <Chip icon={<Cancel />} label="No" size="small" />
              )}
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Device Trust Score
              </Typography>
              <Typography variant="body1">{transaction.device_trust_score}</Typography>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Velocity Last 24h
              </Typography>
              <Typography variant="body1">{transaction.velocity_last_24h}</Typography>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Cardholder Age
              </Typography>
              <Typography variant="body1">{transaction.cardholder_age}</Typography>
            </Grid>
          </Grid>
        </Paper>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Update and Rescore
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Amount"
                value={updateForm.amount ?? ""}
                onChange={(event) => setUpdateForm((prev) => ({ ...prev, amount: Number(event.target.value) }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Transaction Hour"
                value={updateForm.transaction_hour ?? ""}
                onChange={(event) =>
                  setUpdateForm((prev) => ({ ...prev, transaction_hour: Number(event.target.value) }))
                }
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Merchant Category</InputLabel>
                <Select
                  label="Merchant Category"
                  value={updateForm.merchant_category ?? "Electronics"}
                  onChange={(event) =>
                    setUpdateForm((prev) => ({ ...prev, merchant_category: event.target.value }))
                  }
                >
                  <MenuItem value="Electronics">Electronics</MenuItem>
                  <MenuItem value="Travel">Travel</MenuItem>
                  <MenuItem value="Grocery">Grocery</MenuItem>
                  <MenuItem value="Food">Food</MenuItem>
                  <MenuItem value="Clothing">Clothing</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={Boolean(updateForm.foreign_transaction)}
                    onChange={(event) =>
                      setUpdateForm((prev) => ({ ...prev, foreign_transaction: event.target.checked }))
                    }
                  />
                }
                label="Foreign Transaction"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={Boolean(updateForm.location_mismatch)}
                    onChange={(event) =>
                      setUpdateForm((prev) => ({ ...prev, location_mismatch: event.target.checked }))
                    }
                  />
                }
                label="Location Mismatch"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="Device Trust Score"
                value={updateForm.device_trust_score ?? ""}
                onChange={(event) =>
                  setUpdateForm((prev) => ({ ...prev, device_trust_score: Number(event.target.value) }))
                }
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="Velocity Last 24h"
                value={updateForm.velocity_last_24h ?? ""}
                onChange={(event) =>
                  setUpdateForm((prev) => ({ ...prev, velocity_last_24h: Number(event.target.value) }))
                }
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="Cardholder Age"
                value={updateForm.cardholder_age ?? ""}
                onChange={(event) =>
                  setUpdateForm((prev) => ({ ...prev, cardholder_age: Number(event.target.value) }))
                }
              />
            </Grid>
          </Grid>

          <Box sx={{ mt: 2, display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
            <Button variant="contained" onClick={handleUpdateAndRescore} disabled={updateLoading}>
              {updateLoading ? "Updating..." : "Update and Rescore"}
            </Button>
            {updateMessage && (
              <Alert severity={updateMessage.startsWith("Failed") ? "error" : "success"}>{updateMessage}</Alert>
            )}
          </Box>
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Fraud Predictions History
          </Typography>
          {predictions.length === 0 ? (
            <Alert severity="info">No predictions found for this transaction</Alert>
          ) : (
            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              {predictions.map((prediction, index) => (
                <Paper key={prediction.id} variant="outlined" sx={{ p: 2 }}>
                  <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "start", mb: 2 }}>
                    <Box>
                      <Typography variant="subtitle2" color="text.secondary">
                        Prediction #{predictions.length - index}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(prediction.scored_at).toLocaleString()}
                      </Typography>
                    </Box>
                    <Chip
                      label={decisionValue(prediction.decision) === 0 ? "Approved" : "Rejected"}
                      color={decisionValue(prediction.decision) === 0 ? "success" : "error"}
                    />
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  <Grid container spacing={2}>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Fraud Probability
                      </Typography>
                      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <Typography variant="h6">{(prediction.fraud_probability * 100).toFixed(2)}%</Typography>
                        <Chip
                          size="small"
                          label={getFraudColor(prediction.fraud_probability)}
                          color={getFraudColor(prediction.fraud_probability)}
                        />
                      </Box>
                    </Grid>

                    <Grid item xs={6} sm={3}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Model Version
                      </Typography>
                      <Typography variant="body1">N/A</Typography>
                    </Grid>

                    <Grid item xs={6} sm={3}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Threshold
                      </Typography>
                      <Typography variant="body1">{prediction.fraud_probability >= 0.5 ? "0.5" : "0.5"}</Typography>
                    </Grid>

                    <Grid item xs={6} sm={3}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Decision
                      </Typography>
                      <Typography variant="body1">
                        {decisionValue(prediction.decision) === 0 ? "Approve (0)" : "Reject (1)"}
                      </Typography>
                    </Grid>
                  </Grid>
                </Paper>
              ))}
            </Box>
          )}
        </Paper>
      </Container>
    </>
  )
}
