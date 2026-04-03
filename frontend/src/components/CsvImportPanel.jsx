import { useState } from "react";
import api from "../api/client";

export default function CsvImportPanel({ onImported }) {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  const handleFile = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    setMessage("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await api.post("/transactions/import-csv", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMessage(`${data.message} Imported ${data.imported_count} transactions.`);
      onImported?.();
    } catch (uploadError) {
      setError(uploadError.response?.data?.detail || "CSV import failed.");
    } finally {
      event.target.value = "";
      setUploading(false);
    }
  };

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-slate-900">CSV / Bank Statement Import</h2>
      <p className="mt-2 text-sm text-slate-500">Upload a CSV with columns like `date`, `category`, `amount`, `transaction_type`, and `description`.</p>
      <input type="file" accept=".csv" onChange={handleFile} disabled={uploading} className="mt-4 block w-full text-sm text-slate-600" />
      {uploading ? <p className="mt-3 text-sm text-slate-500">Importing transactions...</p> : null}
      {message ? <p className="mt-3 text-sm text-slate-700">{message}</p> : null}
      {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
    </section>
  );
}
