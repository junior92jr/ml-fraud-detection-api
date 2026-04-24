"use client"

import { useState, useEffect } from "react"
import { Container, Grid, Paper, Typography, Box, Chip, CircularProgress, Alert } from "@mui/material"
import { TrendingUp, Warning, Assessment, ModelTraining } from "@mui/icons-material"
import Navigation from "./Navigation"
import { getTransactionById, getTransactions, getTransactionsCount } from "@/lib/api"
import type { FraudPrediction, Transaction } from "@/types/api"

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([])
  const [latestPredictions, setLatestPredictions] = useState<Record<string, FraudPrediction>>({})
  const [totalTransactions, setTotalTransactions] = useState(0)
  const [fraudDetections, setFraudDetections] = useState(0)
  const [avgFraudProbability, setAvgFraudProbability] = useState("0.00")

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)

      try {
        const [total, recent] = await Promise.all([getTransactionsCount(), getTransactions(10, 0)])
        setRecentTransactions(recent)
        setTotalTransactions(total)

        if (recent.length === 0) {
          setFraudDetections(0)
          setAvgFraudProbability("0.00")
          setLatestPredictions({})
          return
        }

        const details = await Promise.all(
          recent.map(async (tx) => ({
            transactionId: tx.transaction_id,
            detail: await getTransactionById(tx.transaction_id),
          })),
        )

        const predictionMap: Record<string, FraudPrediction> = {}
        details.forEach(({ transactionId, detail }) => {
          const latest = detail.predictions[detail.predictions.length - 1]
          if (latest) {
            predictionMap[transactionId] = latest
          }
        })

        const predictionValues = Object.values(predictionMap)
        const detected = predictionValues.filter((p) => p.decision === 1).length
        const avg =
          predictionValues.length === 0
            ? 0
            : predictionValues.reduce((sum, p) => sum + p.fraud_probability, 0) / predictionValues.length

        setLatestPredictions(predictionMap)
        setFraudDetections(detected)
        setAvgFraudProbability((avg * 100).toFixed(2))
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load dashboard data."
        setError(message)
      } finally {
        setLoading(false)
      }
    }

    void load()
  }, [])

  const getFraudColor = (probability: number) => {
    if (probability < 0.3) return "success"
    if (probability < 0.7) return "warning"
    return "error"
  }

  const decisionValue = (decision: number | string | undefined) => Number(decision ?? 1)

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

  if (error) {
    return (
      <>
        <Navigation />
        <Container sx={{ mt: 4 }}>
          <Alert severity="error">{error}</Alert>
        </Container>
      </>
    )
  }

  return (
    <>
      <Navigation />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 3, display: "flex", alignItems: "center", gap: 2 }}>
              <TrendingUp color="primary" sx={{ fontSize: 40 }} />
              <Box>
                <Typography variant="h4">{totalTransactions}</Typography>
                <Typography color="text.secondary">Total Transactions</Typography>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 3, display: "flex", alignItems: "center", gap: 2 }}>
              <Warning color="error" sx={{ fontSize: 40 }} />
              <Box>
                <Typography variant="h4">{fraudDetections}</Typography>
                <Typography color="text.secondary">Fraud Detections</Typography>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 3, display: "flex", alignItems: "center", gap: 2 }}>
              <Assessment color="warning" sx={{ fontSize: 40 }} />
              <Box>
                <Typography variant="h4">{avgFraudProbability}%</Typography>
                <Typography color="text.secondary">Avg Fraud Probability</Typography>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 3, display: "flex", alignItems: "center", gap: 2 }}>
              <ModelTraining color="success" sx={{ fontSize: 40 }} />
              <Box>
                <Typography variant="h4">v1</Typography>
                <Typography color="text.secondary">API Version</Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>

        <Typography variant="h5" gutterBottom>
          Recent Transactions
        </Typography>

        <Paper sx={{ p: 2 }}>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {recentTransactions.map((transaction) => {
              const prediction = latestPredictions[transaction.transaction_id]
              const decision = decisionValue(prediction?.decision) === 0 ? "Approve" : "Reject"
              const probability = prediction?.fraud_probability || 0

              return (
                <Paper
                  key={transaction.id}
                  variant="outlined"
                  sx={{ p: 2, display: "flex", justifyContent: "space-between", alignItems: "center" }}
                >
                  <Box>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {transaction.transaction_id}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      ${transaction.amount.toFixed(2)} - {transaction.merchant_category}
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
                    <Chip
                      label={`${(probability * 100).toFixed(1)}%`}
                      color={getFraudColor(probability)}
                      size="small"
                    />
                    <Chip label={decision} color={decision === "Approve" ? "success" : "error"} variant="outlined" />
                  </Box>
                </Paper>
              )
            })}
          </Box>
        </Paper>
      </Container>
    </>
  )
}
