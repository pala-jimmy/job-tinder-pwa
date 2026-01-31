"use client";

interface CandidateData {
  id: string;
  headline: string;
  location: string;
  bio: string;
  attributes: {
    technical_skills: number;
    communication: number;
    leadership: number;
    problem_solving: number;
    adaptability: number;
    teamwork: number;
  };
  fit_score: number;
}

interface CandidateCardProps {
  candidate: CandidateData;
  style?: React.CSSProperties;
}

export function CandidateCard({ candidate, style }: CandidateCardProps) {
  const attributes = [
    { key: "technical_skills", label: "Tech", color: "bg-blue-500", icon: "" },
    { key: "communication", label: "Comm", color: "bg-green-500", icon: "" },
    { key: "leadership", label: "Lead", color: "bg-purple-500", icon: "" },
    { key: "problem_solving", label: "Problem", color: "bg-orange-500", icon: "" },
    { key: "adaptability", label: "Adapt", color: "bg-pink-500", icon: "" },
    { key: "teamwork", label: "Team", color: "bg-teal-500", icon: "" },
  ];

  // Calculate speedometer colors based on fit score
  const getSpeedometerColor = (score: number) => {
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-blue-500";
    if (score >= 40) return "text-yellow-500";
    return "text-red-500";
  };

  const getFitLabel = (score: number) => {
    if (score >= 80) return "Excellent Fit";
    if (score >= 60) return "Good Fit";
    if (score >= 40) return "Moderate Fit";
    return "Low Fit";
  };

  return (
    <div
      style={style}
      className="bg-white rounded-2xl shadow-2xl overflow-hidden max-w-md w-full"
    >
      {/* Speedometer Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16" />
        <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12" />
        
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-2xl font-bold">Match Score</h3>
            <span className="text-4xl"></span>
          </div>
          <div className={`text-6xl font-bold ${getSpeedometerColor(candidate.fit_score)}`}>
            {candidate.fit_score}%
          </div>
          <p className="text-indigo-100 text-sm mt-1">{getFitLabel(candidate.fit_score)}</p>
        </div>
      </div>

      {/* Candidate Info */}
      <div className="p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-1">
          {candidate.headline}
        </h2>
        <p className="text-gray-500 text-sm mb-4 flex items-center gap-1">
           {candidate.location}
        </p>

        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <p className="text-gray-700 text-sm line-clamp-3">
            {candidate.bio || "No bio provided"}
          </p>
        </div>

        {/* Big Stat Bars - Speedometer Style */}
        <div className="space-y-3">
          <h3 className="text-sm font-bold text-gray-700 uppercase mb-3">
             Performance Metrics
          </h3>
          {attributes.map((attr) => {
            const score = candidate.attributes[attr.key as keyof typeof candidate.attributes];
            const percentage = score;
            
            return (
              <div key={attr.key} className="relative">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{attr.icon}</span>
                    <span className="text-xs font-bold text-gray-700 uppercase">
                      {attr.label}
                    </span>
                  </div>
                  <span className="text-sm font-bold text-gray-900">
                    {score}
                  </span>
                </div>
                
                <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                  <div
                    className={`${attr.color} h-full rounded-full transition-all duration-700 ease-out relative`}
                    style={{ width: `${percentage}%` }}
                  >
                    {/* Shine effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                  </div>
                  
                  {/* Tick marks for speedometer effect */}
                  <div className="absolute inset-0 flex justify-between px-1">
                    {[0, 25, 50, 75, 100].map((tick) => (
                      <div
                        key={tick}
                        className="w-px h-full bg-white/50"
                      />
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
