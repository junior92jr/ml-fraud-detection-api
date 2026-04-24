import TransactionDetails from "@/components/TransactionDetails"

export default async function TransactionDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <TransactionDetails transactionId={id} />
}
