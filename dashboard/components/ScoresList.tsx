"use client"

import { useEffect, useState } from "react"
import {
  Alert,
  Chip,
  CircularProgress,
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  Typography,
} from "@mui/material"
import { useRouter } from "next/navigation"
import Navigation from "./Navigation"
import { getScoresPage } from "@/lib/api"
import type { FraudPrediction } from "@/types/api"

export default function ScoresList() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [scores, setScores] = useState<FraudPrediction[]>([])
  const [totalScores, setTotalScores] = useState(0)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(25)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const offset = page * rowsPerPage
        const { items, total } = await getScoresPage(rowsPerPage, offset)
        setScores(items)
        setTotalScores(total)
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load scores."
        setError(message)
      } finally {
        setLoading(false)
      }
    }

    void load()
  }, [page, rowsPerPage])

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
          Scores History
        </Typography>

        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Score ID</TableCell>
                  <TableCell>Transaction ID</TableCell>
                  <TableCell align="right">Fraud Probability</TableCell>
                  <TableCell align="center">Decision</TableCell>
                  <TableCell>Scored At</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {scores.map((score) => (
                  <TableRow
                    key={score.id}
                    hover
                    onClick={() => router.push(`/transactions/${score.transaction_id}`)}
                    sx={{ cursor: "pointer" }}
                  >
                    <TableCell>{score.id}</TableCell>
                    <TableCell>
                      <Typography color="primary" fontWeight="medium">
                        {score.transaction_id}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{(score.fraud_probability * 100).toFixed(2)}%</TableCell>
                    <TableCell align="center">
                      <Chip
                        label={Number(score.decision) === 0 ? "Approve" : "Reject"}
                        color={Number(score.decision) === 0 ? "success" : "error"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{new Date(score.scored_at).toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <TablePagination
            rowsPerPageOptions={[10, 25, 50, 100]}
            component="div"
            count={totalScores}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={(_event, newPage) => setPage(newPage)}
            onRowsPerPageChange={(event) => {
              setRowsPerPage(Number.parseInt(event.target.value, 10))
              setPage(0)
            }}
          />
        </Paper>
      </Container>
    </>
  )
}
