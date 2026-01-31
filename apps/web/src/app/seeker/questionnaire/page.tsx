"use client";

import { ProtectedRoute } from "@/lib/protected-route";

export default function SeekerQuestionnairePage() {
  return (
    <ProtectedRoute requiredRole="seeker">
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">
            Questionnaire
          </h1>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600">
              Questionnaire interface coming soon...
            </p>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
