"use client"
import { createTheme } from "@mui/material/styles"

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
    success: {
      main: "#2e7d32",
    },
    error: {
      main: "#d32f2f",
    },
    warning: {
      main: "#ed6c02",
    },
  },
  typography: {
    fontFamily: "var(--font-roboto)",
  },
})

export default theme
