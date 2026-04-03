export function formatCurrency(value) {
  const amount = Number(value || 0);
  return `Rs ${amount.toFixed(0)}`;
}

export function formatPercent(value) {
  return `${(Number(value || 0) * 100).toFixed(1)}%`;
}

