"use client"

import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material"
import { Dashboard, Assessment, List, UploadFile, Timeline } from "@mui/icons-material"
import Link from "next/link"
import { usePathname } from "next/navigation"

export default function Navigation() {
  const pathname = usePathname()

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Fraud Detection System
        </Typography>
        <Box sx={{ display: "flex", gap: 1 }}>
          <Button
            color="inherit"
            component={Link}
            href="/"
            startIcon={<Dashboard />}
            sx={{ fontWeight: pathname === "/" ? "bold" : "normal" }}
          >
            Dashboard
          </Button>
          <Button
            color="inherit"
            component={Link}
            href="/score"
            startIcon={<Assessment />}
            sx={{ fontWeight: pathname === "/score" ? "bold" : "normal" }}
          >
            Score Transaction
          </Button>
          <Button
            color="inherit"
            component={Link}
            href="/transactions"
            startIcon={<List />}
            sx={{ fontWeight: pathname.startsWith("/transactions") ? "bold" : "normal" }}
          >
            Transactions
          </Button>
          <Button
            color="inherit"
            component={Link}
            href="/scores"
            startIcon={<Timeline />}
            sx={{ fontWeight: pathname === "/scores" ? "bold" : "normal" }}
          >
            Scores
          </Button>
          <Button
            color="inherit"
            component={Link}
            href="/import"
            startIcon={<UploadFile />}
            sx={{ fontWeight: pathname === "/import" ? "bold" : "normal" }}
          >
            Import CSV
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  )
}
