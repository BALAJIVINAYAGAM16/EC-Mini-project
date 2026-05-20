export default function CreditCard({
  credits
}) {
  return (
    <div className="bg-white shadow rounded-xl p-6">
      <h2 className="text-lg font-semibold">
        Available Credits
      </h2>

      <p className="text-4xl font-bold mt-4 text-indigo-600">
        {credits}
      </p>
    </div>
  );
}