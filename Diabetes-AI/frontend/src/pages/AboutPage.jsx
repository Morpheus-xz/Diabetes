export default function AboutPage() {
  return (
    <div>
      <h1 className="page-title">About</h1>
      <p className="page-subtitle">Project context, methodology, limitations, and social impact.</p>

      <div className="card">
        <h3>Problem Statement</h3>
        <p>
          Diabetes is often identified late. This system shows how AI can support early awareness through risk
          estimation and understandable guidance.
        </p>

        <h3>Objectives</h3>
        <ul>
          <li>Predict diabetes likelihood from common clinical indicators.</li>
          <li>Explain prediction outcomes in simple language.</li>
          <li>Provide safe, educational diabetes-awareness support via chatbot.</li>
        </ul>

        <h3>Methodology</h3>
        <p>
          Data cleaning, missing value handling, exploratory analysis, model comparison (Logistic Regression,
          Decision Tree, Random Forest, SVM), and best model selection by ROC-AUC.
        </p>

        <h3>Limitations</h3>
        <p>This is not a medical device. It does not diagnose disease or replace clinical decision-making.</p>

        <h3>Social Impact & SDGs</h3>
        <p>
          Primary: <strong>SDG 3 (Good Health & Well-Being)</strong>. Also aligned with SDG 9 and SDG 10.
        </p>
      </div>
    </div>
  );
}

