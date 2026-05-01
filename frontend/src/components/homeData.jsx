 import { Zap, TrendingUp, Award, Shield, Clock, Heart } from "lucide-react";

 export const features = [
    { Icon: Zap, title: "AI-Powered Triage", desc: "Rule-based decision engine classifies urgency in milliseconds — no guesswork." },
    { Icon: TrendingUp, title: "Real-time Matching", desc: "Instantly match with available specialists based on your symptom profile." },
    { Icon: Award, title: "Top Specialists", desc: "Access verified, highly-rated doctors across all major medical disciplines." },
    { Icon: Shield, title: "Private & Secure", desc: "Your health data stays on-device. We never share your information." },
    { Icon: Clock, title: "Instant Availability", desc: "See real-time open slots and book in one tap without waiting on hold." },
    { Icon: Heart, title: "Holistic Care", desc: "From diagnosis to follow-up, we keep your entire health journey connected." },
  ];

  export const howItWorks = [
    { step: "01", title: "Describe Symptoms", desc: "Select from common symptoms or type your own. Add severity and duration." },
    { step: "02", title: "AI Analyzes", desc: "Our triage engine classifies urgency and maps to the right specialist." },
    { step: "03", title: "See Reasoning", desc: "Watch each step of the agent's decision-making process in real time." },
    { step: "04", title: "Book Instantly", desc: "Choose a doctor and time slot. Your appointment is confirmed immediately." },
  ];

  export const stats = [
    { value: 50000, suffix: "+", label: "Patients Served" },
    { value: 98, suffix: "%", label: "Accuracy Rate" },
    { value: 200, suffix: "+", label: "Verified Doctors" },
    { value: 30, suffix: "s", label: "Avg Triage Time" },
  ];

  export const predefinedSymptoms = [
    { id: 1, name: "Headache", emoji: "🧠" },
    { id: 2, name: "Chest Pain", emoji: "❤️" },
    { id: 3, name: "Fever", emoji: "🌡️" },
    { id: 4, name: "Cough", emoji: "💨" },
    { id: 5, name: "Fatigue", emoji: "😴" },
    { id: 6, name: "Dizziness", emoji: "🌀" },
    { id: 7, name: "Shortness of Breath", emoji: "🫁" },
    { id: 8, name: "Nausea", emoji: "🤢" },
    { id: 9, name: "Back Pain", emoji: "📍" },
    { id: 10, name: "Sore Throat", emoji: "😣" },
    { id: 11, name: "Chill", emoji: "❄️" },
    { id: 12, name: "Vomiting", emoji: "🤮" },
  ];
  
  export const doctorDB = {
      Cardiologist: [
        { name: "Dr. Rajesh Sharma", specialization: "Cardiologist", rating: 4.9, exp: "14 yrs", slots: ["9:00 AM", "11:30 AM", "3:00 PM"] },
        { name: "Dr. Priya Mehta", specialization: "Cardiologist", rating: 4.7, exp: "10 yrs", slots: ["10:00 AM", "2:00 PM"] },
      ],
      Neurologist: [
        { name: "Dr. Sunita Rao", specialization: "Neurologist", rating: 4.8, exp: "12 yrs", slots: ["9:00 AM", "2:30 PM"] },
        { name: "Dr. Arjun Mehta", specialization: "Neurologist", rating: 4.6, exp: "8 yrs", slots: ["11:00 AM", "4:00 PM"] },
      ],
      Orthopedist: [
        { name: "Dr. Ajay Verma", specialization: "Orthopedist", rating: 4.7, exp: "11 yrs", slots: ["10:30 AM", "1:00 PM", "4:00 PM"] },
      ],
      "General Physician": [
        { name: "Dr. Ritu Gupta", specialization: "General Physician", rating: 4.8, exp: "9 yrs", slots: ["8:30 AM", "12:00 PM", "4:00 PM"] },
        { name: "Dr. Sameer Khan", specialization: "General Physician", rating: 4.6, exp: "7 yrs", slots: ["9:30 AM", "1:30 PM"] },
      ],
    };
