import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-indigo-500 to-purple-600 p-4">
      <div className="w-full max-w-md space-y-8 text-center">
        <div>
          <h1 className="text-5xl font-bold text-white mb-2">
            Job Tinder
          </h1>
          <p className="text-indigo-100 text-lg">
            Match your career
          </p>
        </div>

        <div className="space-y-4 pt-8">
          <Link
            href="/seeker/profile"
            className="block w-full rounded-lg bg-white px-6 py-4 text-lg font-semibold text-indigo-600 shadow-lg hover:bg-indigo-50 transition-colors"
          >
            I am a Job Seeker
          </Link>

          <Link
            href="/offerer/feed"
            className="block w-full rounded-lg border-2 border-white px-6 py-4 text-lg font-semibold text-white hover:bg-white hover:text-indigo-600 transition-colors"
          >
            I am Recruiting
          </Link>
        </div>

        <div className="pt-8 text-indigo-100 text-sm">
          <p>Select your role to continue</p>
        </div>
      </div>
    </div>
  );
}
