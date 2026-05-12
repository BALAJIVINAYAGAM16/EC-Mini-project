export default function AISummaryCard({ title, value }) {
  return (
    <div className="bg-white shadow-md rounded-xl p-6">
      <h2 className="text-gray-500 text-lg">
        {title}
      </h2>

      <p className="text-4xl font-bold mt-3">
        {value}
      </p>
    </div>
  );
}