import { useState } from "react";
import CsvImportPanel from "../components/CsvImportPanel";
import AppLayout from "../layouts/AppLayout";
import TransactionForm from "../components/TransactionForm";

export default function AddTransactionPage() {
  const [message, setMessage] = useState("");

  return (
    <AppLayout title="Add Money" subtitle="Capture income and spending quickly so SaveBud can guide you better.">
      <div className="mx-auto max-w-3xl">
        {message ? <div className="mb-4 rounded-2xl border border-green-500/20 bg-green-500/10 p-4 text-sm text-green-100">{message}</div> : null}
        <TransactionForm
          onSuccess={() => {
            setMessage("Transaction saved successfully.");
            setTimeout(() => setMessage(""), 2500);
          }}
        />
        <div className="mt-6">
          <CsvImportPanel
            onImported={() => {
              setMessage("Transactions imported successfully.");
              setTimeout(() => setMessage(""), 2500);
            }}
          />
        </div>
      </div>
    </AppLayout>
  );
}
