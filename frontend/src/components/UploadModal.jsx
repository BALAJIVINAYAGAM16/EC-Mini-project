import { useState } from "react";
import API from "../api/axios";
import { X, Upload } from "lucide-react";
import { toast } from "../utils/toast";

export default function UploadModal({
  isOpen,
  onClose,
  taskId,
  refreshDocuments,
}) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleUpload = async () => {
    if (!file) {
      toast.error("Please select a file");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();

      formData.append("file", file);
      formData.append("task_id", taskId);

      await API.post(
        "/documents/upload",
        formData,
        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },
        }
      );

      toast.success(
        "Document uploaded successfully"
      );

      setFile(null);

      if (refreshDocuments) {
        refreshDocuments();
      }

      onClose();
    } catch (error) {
      console.error(error);

      toast.error("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white w-full max-w-md rounded-2xl shadow-xl p-6 relative">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-red-500"
        >
          <X size={22} />
        </button>

        {/* Header */}
        <div className="flex items-center gap-2 mb-6">
          <Upload className="text-blue-600" />
          
          <h2 className="text-2xl font-bold">
            Upload Document
          </h2>
        </div>

        {/* File Input */}
        <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center">
          <input
            type="file"
            id="fileUpload"
            className="hidden"
            onChange={(e) =>
              setFile(e.target.files[0])
            }
          />

          <label
            htmlFor="fileUpload"
            className="cursor-pointer"
          >
            <p className="text-gray-600">
              Click to select a file
            </p>

            <p className="text-sm text-gray-400 mt-2">
              PDF, DOCX, PNG, JPG
            </p>
          </label>

          {file && (
            <div className="mt-4 bg-gray-100 rounded-lg p-3 text-sm">
              <p className="font-medium">
                {file.name}
              </p>

              <p className="text-gray-500">
                {(file.size / 1024).toFixed(2)} KB
              </p>
            </div>
          )}
        </div>

        {/* Buttons */}
        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-100"
          >
            Cancel
          </button>

          <button
            onClick={handleUpload}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg"
          >
            {loading
              ? "Uploading..."
              : "Upload"}
          </button>
        </div>
      </div>
    </div>
  );
}
