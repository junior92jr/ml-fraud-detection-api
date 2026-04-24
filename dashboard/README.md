# Fraud Detection API Frontend

A modern, responsive React TypeScript frontend application for a Fraud Detection API built with Next.js 15, Material-UI, and TypeScript.

## Features

- **Dashboard**: View key metrics and recent transactions
- **Score Transaction**: Submit new transactions for fraud scoring
- **Transactions List**: Browse all transactions with pagination
- **Transaction Details**: View detailed information and prediction history
- **Mock API**: Pre-configured with mock data matching the API specification
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Form Validation**: Client-side validation using React Hook Form
- **Material-UI**: Modern, professional design with Material-UI components

## Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Material-UI (MUI) v6** - Modern component library
- **React Hook Form** - Form management and validation
- **MUI X Charts** - Data visualization

## Prerequisites

- Node.js 18+ installed on your machine
- npm or yarn package manager

## Installation

1. Clone or extract the project:
```bash
cd fraud-detection-frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create environment file (optional):
The project includes a `.env.local` file with the default API base URL:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

You can modify this to point to your backend API when it's ready.

## Running the Application

### Development Mode

Run the development server with hot-reload:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Mode

Build and run the production-optimized version:

```bash
# Build the application
npm run build
# or
yarn build

# Start the production server
npm start
# or
yarn start
```

The production server will run on [http://localhost:3000](http://localhost:3000).

## Project Structure

```
├── app/                          # Next.js App Router pages
│   ├── layout.tsx               # Root layout with Material-UI theme
│   ├── page.tsx                 # Dashboard page
│   ├── theme.ts                 # Material-UI theme configuration
│   ├── score/
│   │   └── page.tsx            # Score transaction page
│   └── transactions/
│       ├── page.tsx            # Transactions list page
│       └── [id]/
│           └── page.tsx        # Transaction details page
├── components/                   # React components
│   ├── Dashboard.tsx           # Dashboard component
│   ├── Navigation.tsx          # Navigation bar
│   ├── ScoreTransactionForm.tsx # Transaction scoring form
│   ├── TransactionsList.tsx    # Transactions list with pagination
│   └── TransactionDetails.tsx  # Transaction details view
├── lib/                         # Utility functions and data
│   ├── api.ts                  # API utility functions (ready for backend)
│   └── mockData.ts             # Mock transaction and prediction data
├── types/                       # TypeScript type definitions
│   └── api.ts                  # API request/response types
├── .env.local                   # Environment variables
├── package.json                 # Project dependencies
├── tsconfig.json               # TypeScript configuration
└── README.md                    # This file
```

## API Integration

The application is built to work with mock data but is ready for backend integration:

1. **Mock Data**: Currently uses `lib/mockData.ts` for demonstration
2. **API Functions**: `lib/api.ts` contains ready-to-use API functions
3. **Environment Variable**: Set `NEXT_PUBLIC_API_BASE_URL` to your backend URL

### Connecting to Real Backend

To connect to your backend API:

1. Update `.env.local`:
```
NEXT_PUBLIC_API_BASE_URL=http://your-backend-url:8000
```

2. Replace mock data calls in components with API calls from `lib/api.ts`:

```typescript
// Example: In components/Dashboard.tsx
import { getTransactions } from '@/lib/api';

// Replace mock data
const data = await getTransactions(10, 0);
```

## Pages Overview

### 1. Dashboard (/)
- Displays key metrics: total transactions, fraud detections, average probability, model version
- Shows the 10 most recent transactions with fraud scores
- Color-coded risk indicators (green/yellow/red)

### 2. Score Transaction (/score)
- Form to submit new transactions for fraud scoring
- Client-side validation matching API requirements
- Real-time results display with fraud probability and decision
- All required fields with proper validation

### 3. Transactions List (/transactions)
- Paginated table of all transactions
- Configurable rows per page (10, 25, 50, 100)
- Clickable transaction IDs to view details
- Visual indicators for foreign transactions and location mismatches

### 4. Transaction Details (/transactions/[id])
- Complete transaction information
- Fraud prediction history timeline
- Visual indicators for fraud risk levels
- Back navigation to transactions list

## Form Validation Rules

The Score Transaction form includes validation matching the API specification:

- **Transaction ID**: Required
- **Amount**: Required, must be > 0
- **Transaction Hour**: Required, 0-23
- **Merchant Category**: Required, dropdown selection
- **Device Trust Score**: Required, 0-100
- **Velocity Last 24h**: Required, >= 0
- **Cardholder Age**: Required, 18-100

## Color Coding

The application uses consistent color coding for fraud risk:

- **Green**: Low risk (probability < 30%)
- **Yellow/Orange**: Medium risk (probability 30-70%)
- **Red**: High risk (probability > 70%)

## Customization

### Changing Theme Colors

Edit `app/theme.ts` to customize the Material-UI theme:

```typescript
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    // Add more customization
  },
});
```

### Modifying Mock Data

Edit `lib/mockData.ts` to change sample transactions and predictions.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Port Already in Use

If port 3000 is already in use, you can specify a different port:

```bash
PORT=3001 npm run dev
```

### Module Not Found Errors

Clear the Next.js cache and reinstall dependencies:

```bash
rm -rf .next node_modules
npm install
npm run dev
```

## Future Enhancements

- Real-time updates using WebSocket
- Advanced filtering and search
- CSV export functionality
- Dark mode toggle
- Advanced analytics and charts
- Batch transaction scoring

## License

This project is provided as-is for demonstration purposes.
