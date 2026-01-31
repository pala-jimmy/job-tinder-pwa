"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/lib/protected-route";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

interface ProfileData {
  headline: string;
  location: string;
  bio: string;
  preferences: {
    remote_ok: boolean;
    willing_to_relocate: boolean;
    expected_salary_min?: number;
    expected_salary_max?: number;
  };
}

type SaveState = "idle" | "saving" | "saved" | "error";

export default function SeekerProfilePage() {
  return (
    <ProtectedRoute requiredRole="seeker">
      <ProfileForm />
    </ProtectedRoute>
  );
}

function ProfileForm() {
  const router = useRouter();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [profile, setProfile] = useState<ProfileData>({
    headline: "",
    location: "",
    bio: "",
    preferences: {
      remote_ok: false,
      willing_to_relocate: false,
    },
  });

  // Load existing profile
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await api.get<ProfileData>("/seeker/profile");
        setProfile(data);
      } catch (err) {
        console.error("Failed to load profile:", err);
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, []);

  // Autosave with debouncing
  useEffect(() => {
    if (loading) return;

    const timeoutId = setTimeout(async () => {
      setSaveState("saving");
      try {
        await api.put("/seeker/profile", profile);
        setSaveState("saved");
        setTimeout(() => setSaveState("idle"), 2000);
      } catch (err) {
        console.error("Failed to save profile:", err);
        setSaveState("error");
        setTimeout(() => setSaveState("idle"), 3000);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [profile, loading]);

  const updateField = useCallback((field: keyof ProfileData, value: any) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
  }, []);

  const updatePreference = useCallback((key: string, value: any) => {
    setProfile((prev) => ({
      ...prev,
      preferences: { ...prev.preferences, [key]: value },
    }));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg text-gray-600">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Edit Profile</h1>
          <div className="flex items-center gap-2">
            {saveState === "saving" && (
              <span className="text-sm text-gray-500">Saving...</span>
            )}
            {saveState === "saved" && (
              <span className="text-sm text-green-600"> Saved</span>
            )}
            {saveState === "error" && (
              <span className="text-sm text-red-600">Error saving</span>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div>
            <label htmlFor="headline" className="block text-sm font-medium text-gray-700 mb-2">
              Professional Headline
            </label>
            <input
              id="headline"
              type="text"
              value={profile.headline}
              onChange={(e) => updateField("headline", e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="e.g., Senior Full Stack Developer"
            />
          </div>

          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
              Location
            </label>
            <input
              id="location"
              type="text"
              value={profile.location}
              onChange={(e) => updateField("location", e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="e.g., San Francisco, CA"
            />
          </div>

          <div>
            <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-2">
              Bio
            </label>
            <textarea
              id="bio"
              value={profile.bio}
              onChange={(e) => updateField("bio", e.target.value)}
              rows={5}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Tell us about yourself, your experience, and what you're looking for..."
            />
          </div>

          <div className="border-t pt-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Preferences</h2>

            <div className="space-y-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={profile.preferences.remote_ok}
                  onChange={(e) => updatePreference("remote_ok", e.target.checked)}
                  className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <span className="text-sm text-gray-700">Open to remote work</span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={profile.preferences.willing_to_relocate}
                  onChange={(e) => updatePreference("willing_to_relocate", e.target.checked)}
                  className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <span className="text-sm text-gray-700">Willing to relocate</span>
              </label>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="salary_min" className="block text-sm font-medium text-gray-700 mb-2">
                    Min Salary ($)
                  </label>
                  <input
                    id="salary_min"
                    type="number"
                    value={profile.preferences.expected_salary_min || ""}
                    onChange={(e) => updatePreference("expected_salary_min", e.target.value ? parseInt(e.target.value) : undefined)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="80000"
                  />
                </div>
                <div>
                  <label htmlFor="salary_max" className="block text-sm font-medium text-gray-700 mb-2">
                    Max Salary ($)
                  </label>
                  <input
                    id="salary_max"
                    type="number"
                    value={profile.preferences.expected_salary_max || ""}
                    onChange={(e) => updatePreference("expected_salary_max", e.target.value ? parseInt(e.target.value) : undefined)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="120000"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-4 pt-4">
            <button
              onClick={() => router.push("/")}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
            >
              Back to Home
            </button>
            <button
              onClick={() => router.push("/seeker/questionnaire")}
              className="flex-1 bg-indigo-600 text-white py-2 px-6 rounded-lg font-semibold hover:bg-indigo-700 transition"
            >
              Continue to Questionnaire 
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
