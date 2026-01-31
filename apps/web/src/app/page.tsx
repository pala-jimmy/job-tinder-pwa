"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function Home() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 p-4">
      <div className="max-w-2xl w-full text-center text-white space-y-8">
        <h1 className="text-5xl md:text-6xl font-bold">
          Job Tinder
        </h1>
        <p className="text-xl md:text-2xl opacity-90">
          Match your career. Swipe to find your perfect job or candidate.
        </p>

        {user ? (
          <div className="space-y-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
              <p className="text-lg mb-2">Welcome back!</p>
              <p className="text-2xl font-semibold">{user.email}</p>
              <p className="text-sm opacity-75 mt-1 capitalize">{user.role}</p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {user.role === "seeker" ? (
                <>
                  <Link 
                    href="/seeker/profile"
                    className="bg-white text-indigo-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-100 transition"
                  >
                    Edit Profile
                  </Link>
                  <Link 
                    href="/seeker/questionnaire"
                    className="bg-white/20 backdrop-blur-sm text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white/30 transition"
                  >
                    Questionnaire
                  </Link>
                  <Link 
                    href="/seeker/stats"
                    className="bg-white/20 backdrop-blur-sm text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white/30 transition"
                  >
                    View Stats
                  </Link>
                </>
              ) : (
                <>
                  <Link 
                    href="/offerer/role-select"
                    className="bg-white text-indigo-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-100 transition"
                  >
                    Select Role
                  </Link>
                  <Link 
                    href="/offerer/feed"
                    className="bg-white/20 backdrop-blur-sm text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white/30 transition"
                  >
                    Browse Candidates
                  </Link>
                  <Link 
                    href="/offerer/shortlist"
                    className="bg-white/20 backdrop-blur-sm text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white/30 transition"
                  >
                    Shortlist
                  </Link>
                </>
              )}
            </div>

            <button
              onClick={logout}
              className="text-white/75 hover:text-white underline text-sm"
            >
              Log out
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            <p className="text-lg opacity-90">
              Get started by creating an account or logging in
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href="/auth/register"
                className="bg-white text-indigo-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-100 transition"
              >
                Sign Up
              </Link>
              <Link 
                href="/auth/login"
                className="bg-white/20 backdrop-blur-sm text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white/30 transition border-2 border-white/30"
              >
                Log In
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
