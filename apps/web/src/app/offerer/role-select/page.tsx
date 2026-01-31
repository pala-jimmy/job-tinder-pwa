"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/lib/protected-route";
import { api } from "@/lib/api";

interface RoleTemplate {
  id: string;
  role_name: string;
  description: string;
  key_attributes: string[];
}

export default function RoleSelectPageWrapper() {
  return (
    <ProtectedRoute requiredRole="offerer">
      <RoleSelectPage />
    </ProtectedRoute>
  );
}

function RoleSelectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [roles, setRoles] = useState<RoleTemplate[]>([]);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [currentRole, setCurrentRole] = useState<string | null>(null);

  useEffect(() => {
    const loadRoles = async () => {
      try {
        // Load available role templates
        const rolesData = await api.get<RoleTemplate[]>("/offerer/roles");
        setRoles(rolesData);

        // Load current selected role
        try {
          const config = await api.get<{ role_id: string }>("/offerer/role-config");
          setCurrentRole(config.role_id);
          setSelectedRole(config.role_id);
        } catch (err) {
          // No role selected yet
          console.log("No role configured yet");
        }
      } catch (err) {
        console.error("Failed to load roles:", err);
      } finally {
        setLoading(false);
      }
    };
    loadRoles();
  }, []);

  const handleSaveRole = async () => {
    if (!selectedRole) return;

    setSaving(true);
    try {
      await api.post("/offerer/role-config", { role_id: selectedRole });
      setCurrentRole(selectedRole);
      router.push("/offerer/feed");
    } catch (err) {
      console.error("Failed to save role:", err);
      alert("Failed to save role selection");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg text-gray-600">Loading roles...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Select Role Template
          </h1>
          <p className="text-gray-600">
            Choose the role you&apos;re hiring for. This will customize your candidate feed.
          </p>
          {currentRole && (
            <p className="text-sm text-indigo-600 mt-2">
              Currently viewing candidates for: <strong>{roles.find(r => r.id === currentRole)?.role_name}</strong>
            </p>
          )}
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
          {roles.map((role) => {
            const isSelected = selectedRole === role.id;
            const isCurrent = currentRole === role.id;

            return (
              <button
                key={role.id}
                onClick={() => setSelectedRole(role.id)}
                className={`relative text-left p-6 rounded-xl border-2 transition-all ${
                  isSelected
                    ? "border-indigo-500 bg-indigo-50 shadow-lg scale-105"
                    : "border-gray-200 bg-white hover:border-indigo-300 hover:shadow-md"
                }`}
              >
                {isCurrent && (
                  <span className="absolute top-3 right-3 px-2 py-1 text-xs font-semibold bg-green-100 text-green-700 rounded-full">
                    Active
                  </span>
                )}

                <h3 className="text-xl font-bold text-gray-800 mb-2">
                  {role.role_name}
                </h3>

                <p className="text-sm text-gray-600 mb-4">
                  {role.description}
                </p>

                <div className="space-y-2">
                  <p className="text-xs font-semibold text-gray-700 uppercase">
                    Key Attributes:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {role.key_attributes.map((attr, idx) => (
                      <span
                        key={idx}
                        className={`px-2 py-1 text-xs font-medium rounded-full ${
                          isSelected
                            ? "bg-indigo-200 text-indigo-800"
                            : "bg-gray-100 text-gray-700"
                        }`}
                      >
                        {attr}
                      </span>
                    ))}
                  </div>
                </div>

                {isSelected && (
                  <div className="absolute inset-0 rounded-xl border-4 border-indigo-500 pointer-events-none" />
                )}
              </button>
            );
          })}
        </div>

        <div className="flex gap-4">
          <button
            onClick={() => router.push("/")}
            className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
          >
            Back to Home
          </button>
          <button
            onClick={handleSaveRole}
            disabled={!selectedRole || saving || selectedRole === currentRole}
            className="flex-1 bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? "Saving..." : selectedRole === currentRole ? "Continue to Feed" : "Save & View Candidates"}
          </button>
        </div>
      </div>
    </div>
  );
}
