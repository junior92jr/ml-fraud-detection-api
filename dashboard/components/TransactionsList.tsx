"use client"

import type React from "react"

import { useState, useEffect } from "react"
import {
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  CircularProgress,
  Alert,
} from "@mui/material"
import { CheckCircle, Cancel } from "@mui/icons-material"
import { useRouter } from "next/navigation"
import Navigation from "./Navigation"
import type { Transaction } from "@/types/api"
import { getTransactionsPage } from "@/lib/api"

export default function TransactionsList() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [totalTransactions, setTotalTransactions] = useState(0)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const offset = page * rowsPerPage
        const { items, total } = await getTransactionsPage(rowsPerPage, offset)
        setTransactions(items)
        setTotalTransactions(total)
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load transactions."
        setError(message)
      } finally {
        setLoading(false)
      }
    }

    void load()
  }, [page, rowsPerPage])

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(Number.parseInt(event.target.value, 10))
    setPage(0)
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
          Transactions List
        </Typography>

        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Transaction ID</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell>Merchant Category</TableCell>
                  <TableCell align="center">Transaction Hour</TableCell>
                  <TableCell align="center">Foreign</TableCell>
                  <TableCell align="center">Location Mismatch</TableCell>
                  <TableCell align="right">Device Trust</TableCell>
                  <TableCell align="right">Velocity 24h</TableCell>
                  <TableCell align="right">Age</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {transactions.map((transaction) => (
                  <TableRow
                    key={transaction.id}
                    hover
                    onClick={() => router.push(`/transactions/${transaction.transaction_id}`)}
                    sx={{
                      textDecoration: "none",
                      cursor: "pointer",
                      "&:hover": {
                        backgroundColor: "action.hover",
                      },
                    }}
                  >
                    <TableCell>
                      <Typography color="primary" fontWeight="medium">
                        {transaction.transaction_id}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">${transaction.amount.toFixed(2)}</TableCell>
                    <TableCell>{transaction.merchant_category}</TableCell>
                    <TableCell align="center">{transaction.transaction_hour}</TableCell>
                    <TableCell align="center">
                      {transaction.foreign_transaction ? (
                        <Chip icon={<CheckCircle />} label="Yes" color="warning" size="small" />
                      ) : (
                        <Chip icon={<Cancel />} label="No" size="small" />
                      )}
                    </TableCell>
                    <TableCell align="center">
                      {transaction.location_mismatch ? (
                        <Chip icon={<CheckCircle />} label="Yes" color="warning" size="small" />
                      ) : (
                        <Chip icon={<Cancel />} label="No" size="small" />
                      )}
                    </TableCell>
                    <TableCell align="right">{transaction.device_trust_score}</TableCell>
                    <TableCell align="right">{transaction.velocity_last_24h}</TableCell>
                    <TableCell align="right">{transaction.cardholder_age}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[10, 25, 50, 100]}
            component="div"
            count={totalTransactions}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      </Container>
    </>
  )
}
