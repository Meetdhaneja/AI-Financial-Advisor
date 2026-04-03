import { useEffect, useState } from "react";
import api from "../api/client";
import BudgetPreferencesForm from "../components/BudgetPreferencesForm";
import GoalPlanner from "../components/GoalPlanner";
import RecurringBillsPanel from "../components/RecurringBillsPanel";
import ScenarioSimulator from "../components/ScenarioSimulator";
import { useAuth } from "../contexts/AuthContext";
import AppLayout from "../layouts/AppLayout";

export default function PlanningPage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(user);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadPlanning = async () => {
    setLoading(true);
    setError("");
    try {
      const [profileRes, goalsRes] = await Promise.all([api.get("/auth/me"), api.get("/ai/goals")]);
      setProfile(profileRes.data);
      setGoals(goalsRes.data);
    } catch {
      setError("Could not load your planning tools right now.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlanning();
  }, []);

  return (
    <AppLayout
      title="Planning"
      subtitle="Set your monthly plan, track goals, manage recurring bills, and try simple what-if scenarios."
    >
      {error ? <div className="mb-6 rounded-3xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">{error}</div> : null}
      {loading && !profile ? <div className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 text-slate-300">Loading planning tools...</div> : null}

      <div className="grid gap-6">
        <BudgetPreferencesForm user={profile} onSaved={(updatedUser) => setProfile(updatedUser)} />
        <div className="grid gap-6 xl:grid-cols-2">
          <GoalPlanner goals={goals} onRefresh={loadPlanning} />
          <RecurringBillsPanel onRefresh={loadPlanning} />
        </div>
        <ScenarioSimulator />
      </div>
    </AppLayout>
  );
}
