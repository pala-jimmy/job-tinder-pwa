"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/lib/protected-route";
import { api } from "@/lib/api";

interface Question {
  id: string;
  question_text: string;
  question_type: "single_choice" | "scale" | "multiple_choice" | "text";
  options?: string[];
  category: string;
}

interface Answer {
  question_id: string;
  answer_value: string | number | string[];
}

type SaveState = "idle" | "saving" | "saved" | "error";

export default function QuestionnairePageWrapper() {
  return (
    <ProtectedRoute requiredRole="seeker">
      <QuestionnairePage />
    </ProtectedRoute>
  );
}

function QuestionnairePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<string, Answer>>({});
  const [currentStep, setCurrentStep] = useState(0);
  const [saveState, setSaveState] = useState<SaveState>("idle");

  // Load questions and existing answers
  useEffect(() => {
    const loadQuestionnaire = async () => {
      try {
        const questionsData = await api.get<Question[]>("/questionnaire");
        setQuestions(questionsData);

        // Load existing answers
        try {
          const answersData = await api.get<Answer[]>("/questionnaire/answers");
          const answersMap = answersData.reduce((acc, answer) => {
            acc[answer.question_id] = answer;
            return acc;
          }, {} as Record<string, Answer>);
          setAnswers(answersMap);
        } catch (err) {
          // No existing answers, that's fine
          console.log("No existing answers found");
        }
      } catch (err) {
        console.error("Failed to load questionnaire:", err);
      } finally {
        setLoading(false);
      }
    };
    loadQuestionnaire();
  }, []);

  // Autosave answer when it changes
  const saveAnswer = async (questionId: string, value: string | number | string[]) => {
    const answer: Answer = {
      question_id: questionId,
      answer_value: value,
    };

    setAnswers((prev) => ({ ...prev, [questionId]: answer }));
    setSaveState("saving");

    try {
      await api.post("/questionnaire/answers", [answer]);
      setSaveState("saved");
      setTimeout(() => setSaveState("idle"), 1500);
    } catch (err) {
      console.error("Failed to save answer:", err);
      setSaveState("error");
      setTimeout(() => setSaveState("idle"), 2000);
    }
  };

  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    router.push("/seeker/stats");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg text-gray-600">Loading questionnaire...</div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-gray-600 mb-4">No questions available</p>
          <button
            onClick={() => router.push("/")}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentStep];
  const progress = ((currentStep + 1) / questions.length) * 100;
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Header with progress */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-2xl font-bold text-gray-800">Questionnaire</h1>
            <div className="text-sm text-gray-600">
              {currentStep + 1} / {questions.length}
            </div>
          </div>
          
          {/* Progress bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          
          <div className="flex items-center justify-between mt-2">
            <span className="text-sm text-gray-500">
              {answeredCount} of {questions.length} answered
            </span>
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

        {/* Question card */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="mb-4">
            <span className="text-sm font-medium text-indigo-600 uppercase">
              {currentQuestion.category}
            </span>
          </div>
          
          <h2 className="text-xl font-semibold text-gray-800 mb-6">
            {currentQuestion.question_text}
          </h2>

          <QuestionInput
            question={currentQuestion}
            value={answers[currentQuestion.id]?.answer_value}
            onChange={(value) => saveAnswer(currentQuestion.id, value)}
          />
        </div>

        {/* Navigation buttons */}
        <div className="flex gap-4">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
             Previous
          </button>
          
          {currentStep < questions.length - 1 ? (
            <button
              onClick={handleNext}
              className="flex-1 bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 transition"
            >
              Next 
            </button>
          ) : (
            <button
              onClick={handleComplete}
              className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition"
            >
              Complete & View Stats
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// Question input component based on type
function QuestionInput({
  question,
  value,
  onChange,
}: {
  question: Question;
  value: string | number | string[] | undefined;
  onChange: (value: string | number | string[]) => void;
}) {
  switch (question.question_type) {
    case "single_choice":
      return (
        <div className="space-y-3">
          {question.options?.map((option) => (
            <label
              key={option}
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-indigo-300 transition"
            >
              <input
                type="radio"
                name={question.id}
                value={option}
                checked={value === option}
                onChange={(e) => onChange(e.target.value)}
                className="w-5 h-5 text-indigo-600 border-gray-300 focus:ring-indigo-500"
              />
              <span className="text-gray-700">{option}</span>
            </label>
          ))}
        </div>
      );

    case "scale":
      return (
        <div className="space-y-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Strongly Disagree</span>
            <span>Strongly Agree</span>
          </div>
          <input
            type="range"
            min="1"
            max="5"
            value={typeof value === "number" ? value : 3}
            onChange={(e) => onChange(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
          />
          <div className="flex justify-between text-xs text-gray-500">
            {[1, 2, 3, 4, 5].map((num) => (
              <span key={num}>{num}</span>
            ))}
          </div>
          <div className="text-center text-lg font-semibold text-indigo-600 mt-4">
            Selected: {typeof value === "number" ? value : 3}
          </div>
        </div>
      );

    case "multiple_choice":
      const selectedValues = Array.isArray(value) ? value : [];
      return (
        <div className="space-y-3">
          {question.options?.map((option) => (
            <label
              key={option}
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-indigo-300 transition"
            >
              <input
                type="checkbox"
                value={option}
                checked={selectedValues.includes(option)}
                onChange={(e) => {
                  if (e.target.checked) {
                    onChange([...selectedValues, option]);
                  } else {
                    onChange(selectedValues.filter((v) => v !== option));
                  }
                }}
                className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <span className="text-gray-700">{option}</span>
            </label>
          ))}
        </div>
      );

    case "text":
      return (
        <textarea
          value={typeof value === "string" ? value : ""}
          onChange={(e) => onChange(e.target.value)}
          rows={5}
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
          placeholder="Type your answer here..."
        />
      );

    default:
      return null;
  }
}
