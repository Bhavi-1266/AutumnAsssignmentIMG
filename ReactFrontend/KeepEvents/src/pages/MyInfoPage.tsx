import NavBar from "../components/navBar";
import { getMe } from "../services/auth";
import { patchUserData, patchUserProfileImage } from "../services/user";
import { useEffect, useRef, useState } from "react";
import type { User , EditedData } from "../types/user";
import { Pencil, Eraser, Save, X } from "lucide-react";





function MyInfoPage() {
  const [user, setUser] = useState<User | null>(null);
  const [editData, setEditData] = useState<EditedData>({});
  const [editingField, setEditingField] =useState<keyof EditedData | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [loading, setLoading] = useState(true);
  const [profileImageFile, setProfileImageFile] = useState<File | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getMe();
        setUser(data.user);
        setEditData(data.user);
      } catch {
        window.location.href = "/login";
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const updateField = (field: keyof User, value: any) => {
    setEditData(prev => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const onProfileImageSelect = (file: File) => {
    setProfileImageFile(file);
    updateField("userProfile", URL.createObjectURL(file)); // preview only
    setEditingField("userProfile");
  };

  const revertField = (field: keyof User) => {
    if (!user) return;
    setEditData(prev => ({ ...prev, [field]: user[field] }));
    if (field === "userProfile") setProfileImageFile(null);
    setEditingField(null);
  };

  const discardChanges = () => {
    if (!user) return;
    setEditData(user);
    setProfileImageFile(null);
    setEditingField(null);
    setHasChanges(false);
  };

  const saveChanges = async () => {
  if (!user) return;

  try {
    // 1️⃣ Update profile image first (if changed)
    if (profileImageFile) {
      await patchUserProfileImage(user.userid, profileImageFile);
    }

    // 2️⃣ Update text data
    const res = await patchUserData(user.userid, editData);

    setUser(res);
    setEditData(res);
    setProfileImageFile(null);
    setEditingField(null);
    setHasChanges(false);
  } catch (err) {
    console.error(err);
    alert("Failed to save profile");
  }
};


  if (loading) {
    return (
      <>
        <NavBar />
        <p className="p-6">Loading profile...</p>
      </>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-100">
      <NavBar />

      <div className="max-w-4xl mx-auto p-6 space-y-6">

        {/* Profile Header */}
        <div className="bg-white shadow rounded p-6 flex items-center space-x-8">
          <div className="relative">
            <img
              src={editData.userProfile || "../../src/assets/ProfileFace.png"}
              className="w-36 h-36 rounded-full object-cover border"
            />

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              hidden
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  onProfileImageSelect(e.target.files[0]);
                }
              }}
            />

            <FieldIcon
              editing={editingField === "userProfile"}
              onEdit={() => fileInputRef.current?.click()}
              onRevert={() => revertField("userProfile")}
            />
          </div>

          <div className="space-y-2 w-full">
            <EditableInput
              label="Username"
              field="username"
              value={user.username}
            />
            <p className="text-gray-500">{user.email}</p>
          </div>
        </div>

        <EditableInput
          label="About"
          field="userbio"
          value={editData.userbio}
          editingField={editingField}
          onEdit={setEditingField}
          onChange={updateField}
          onRevert={revertField}
          multiline
        />

        <div className="grid grid-cols-2 gap-6">
          <EditableInput label="Enrollment No" field="enrollmentNo" value={editData.enrollmentNo} {...editableProps} />
          <EditableInput label="Department" field="dept" value={editData.dept} {...editableProps} />
          <EditableInput label="Batch" field="batch" value={editData.batch} {...editableProps} />
        </div>
      </div>

      {hasChanges && (
        <div className="fixed bottom-6 right-6 flex gap-3">
          <button onClick={discardChanges} className="bg-gray-200 px-4 py-2 rounded">
            <X size={16} /> Discard
          </button>
          <button onClick={saveChanges} className="bg-green-600 text-white px-4 py-2 rounded">
            <Save size={16} /> Save
          </button>
        </div>
      )}
    </div>
  );
}

export default MyInfoPage;

/* ================= Components ================= */

const editableProps = {
  editingField: null,
  onEdit: () => {},
  onChange: () => {},
  onRevert: () => {},
};

function FieldIcon({ editing, onEdit, onRevert }: any) {
  return (
    <button
      onClick={editing ? onRevert : onEdit}
      className={`absolute bottom-1 right-1 p-2 rounded-full ${
        editing ? "bg-red-100 text-red-600" : "bg-white"
      }`}
    >
      {editing ? <Eraser size={12} /> : <Pencil size={12} />}
    </button>
  );
}

function EditableInput({ label, field, value, editingField, onEdit, onChange, onRevert, multiline = false }: any) {
  const isEditing = editingField === field;

  return (
    <div className="relative bg-white shadow rounded p-6">
      <p className="text-sm text-gray-500">{label}</p>
      {isEditing ? (
        multiline ? (
          <textarea value={value ?? ""} onChange={(e) => onChange(field, e.target.value)} className="w-full border p-2" />
        ) : (
          <input value={value ?? ""} onChange={(e) => onChange(field, e.target.value)} className="w-full border p-2" />
        )
      ) : (
        <p className="font-medium">{value ?? "Empty"}</p>
      )}
      <FieldIcon editing={isEditing} onEdit={() => onEdit(field)} onRevert={() => onRevert(field)} />
    </div>
  );
}
