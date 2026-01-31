"use client";

import { ProtectedRoute } from "@/lib/protected-route";

export default function SeekerProfilePage() {
  return (
    <ProtectedRoute requiredRole="seeker">
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">
            Profile
          </h1>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600">
              Profile editing interface coming soon...
            </p>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
