export default function PlanCard({
  title,
  price,
  credits,
  features,
  onSelect
}) {
  return (
    <div className="bg-white rounded-2xl shadow p-8">
      <h2 className="text-2xl font-bold">
        {title}
      </h2>

      <p className="text-4xl font-bold mt-4">
        ₹{price}
      </p>

      <p className="mt-2 text-gray-500">
        {credits} Credits
      </p>

      <div className="mt-6 flex flex-col gap-2">
        {features.map((feature) => (
          <p key={feature}>
            • {feature}
          </p>
        ))}
      </div>

      <button
        onClick={onSelect}
        className="mt-8 w-full bg-indigo-600 text-white py-3 rounded-lg"
      >
        Choose Plan
      </button>
    </div>
  );
}