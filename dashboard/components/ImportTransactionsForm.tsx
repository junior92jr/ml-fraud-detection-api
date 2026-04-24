"use client"

import { useState } from "react"
import {
  Alert,
  Box,
  Button,
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material"
import { UploadFile } from "@mui/icons-material"
import Navigation from "./Navigation"
import { importTransactionsCsv } from "@/lib/api"
import type { TransactionImportResponse } from "@/types/api"

export default function ImportTransactionsForm() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<TransactionImportResponse | null>(null)

  const handleImport = async () => {
    if (!file) {
      setError("Please select a CSV file.")
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await importTransactionsCsv(file)
      setResult(response)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to import transactions."
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Navigation />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Import Transactions CSV
        </Typography>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
            <Button variant="outlined" component="label">
              Select CSV
              <input
                hidden
                type="file"
                accept=".csv,text/csv"
                onChange={(event) => setFile(event.target.files?.[0] || null)}
              />
            </Button>

            <Typography variant="body2" color="text.secondary">
              {file ? file.name : "No file selected"}
            </Typography>

            <Button
              variant="contained"
              startIcon={<UploadFile />}
              onClick={handleImport}
              disabled={loading || !file}
            >
              {loading ? "Importing..." : "Import"}
            </Button>
          </Box>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {result && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Import Summary
            </Typography>
            <Box sx={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 2, mb: 3 }}>
              <Typography>Total Rows: {result.total_rows}</Typography>
              <Typography>Imported: {result.imported}</Typography>
              <Typography>Duplicates: {result.skipped_duplicates}</Typography>
              <Typography>Invalid: {result.skipped_invalid}</Typography>
              <Typography>Scoring Errors: {result.skipped_scoring_errors}</Typography>
            </Box>

            {result.errors.length > 0 && (
              <>
                <Typography variant="subtitle1" gutterBottom>
                  Errors
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Line</TableCell>
                        <TableCell>Transaction ID</TableCell>
                        <TableCell>Error</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {result.errors.slice(0, 200).map((entry, index) => (
                        <TableRow key={`${entry.line}-${entry.transaction_id || "na"}-${index}`}>
                          <TableCell>{entry.line}</TableCell>
                          <TableCell>{entry.transaction_id || "-"}</TableCell>
                          <TableCell>{entry.error}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            )}
          </Paper>
        )}
      </Container>
    </>
  )
}
