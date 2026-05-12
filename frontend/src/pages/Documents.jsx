import { useCallback, useEffect, useState } from "react";
import API from "../api/axios";
import Sidebar from "../components/Sidebar";
import NotificationBell from "../components/NotificationBell";
import { toast } from "../utils/toast";
import { useAuth } from "../context/auth-context";

export default function Documents() {
  const { user, fetchUser } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedTaskId, setSelectedTaskId] = useState(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      const res = await API.get("/documents/");
      setDocuments(res.data);
    } catch {
      toast.error("Failed to fetch documents");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    if (!user) {
      fetchUser();
    }

    API.get("/documents/")
      .then((res) => {
        if (isMounted) {
          setDocuments(res.data);
        }
      })
      .catch(() => {
        toast.error("Failed to fetch documents");
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [user, fetchUser, fetchDocuments]);

  const handleUpload = async () => {
    if (!file) {
      toast.warning("Please select a file");
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);
      if (selectedTaskId) {
        formData.append("task_id", selectedTaskId);
      }

      await API.post("/documents/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      toast.success("Document uploaded successfully!");
      setFile(null);
      setSelectedTaskId(null);
      document.getElementById("fileInput").value = "";
      fetchDocuments();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (docId, fileName) => {
    try {
      const res = await API.get(`/documents/${docId}/download`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", fileName);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      toast.success("Document downloaded");
    } catch {
      toast.error("Download failed");
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm("Are you sure you want to delete this document?")) {
      return;
    }

    try {
      await API.delete(`/documents/${docId}`);
      toast.success("Document deleted successfully");
      fetchDocuments();
    } catch {
      toast.error("Failed to delete document");
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString() + " " + new Date(dateString).toLocaleTimeString();
  };

  return (
    <div className="flex">
      <Sidebar />

      <div className="flex-1 p-6 bg-gray-50">
        <div className="mb-6 flex items-center justify-between gap-4">
          <h1 className="text-3xl font-bold">Document Management</h1>
          <NotificationBell />
        </div>

        {/* Upload Section */}
        <div className="bg-white p-6 rounded-xl shadow-md mb-6">
          <h2 className="text-xl font-semibold mb-4">Upload New Document</h2>
          <div className="flex gap-4">
            <input
              id="fileInput"
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Choose a file"
              disabled={uploading}
            />
            <input
              type="number"
              value={selectedTaskId || ""}
              onChange={(e) => setSelectedTaskId(e.target.value ? parseInt(e.target.value) : null)}
              className="border border-gray-300 rounded-lg px-3 py-2 w-32 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Task ID (optional)"
              disabled={uploading}
            />
            <button
              onClick={handleUpload}
              disabled={uploading}
              className={`${
                uploading
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700"
              } text-white px-6 py-2 rounded-lg transition`}
            >
              {uploading ? "Uploading..." : "Upload"}
            </button>
          </div>
        </div>

        {/* Documents List */}
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          <div className="px-6 py-4 bg-gray-100 border-b">
            <h2 className="text-lg font-semibold">My Documents</h2>
            <p className="text-sm text-gray-600">Total: {documents.length}</p>
          </div>

          {loading ? (
            <div className="p-6 text-center">
              <p className="text-gray-500">Loading documents...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="p-6 text-center">
              <p className="text-gray-500">No documents found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">File Name</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Version</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Uploaded By</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Date</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id} className="border-b hover:bg-gray-50 transition">
                      <td className="px-6 py-4 text-sm">{doc.file_name}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">v{doc.version}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">{doc.uploaded_by}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">{formatDate(doc.created_at)}</td>
                      <td className="px-6 py-4 text-sm">
                        <button
                          onClick={() => handleDownload(doc.id, doc.file_name)}
                          className="text-blue-600 hover:text-blue-800 mr-4 font-medium"
                        >
                          📥 Download
                        </button>
                        {user?.role !== "employee" && (
                          <button
                            onClick={() => handleDelete(doc.id)}
                            className="text-red-600 hover:text-red-800 font-medium"
                          >
                            🗑️ Delete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
