// components/KanbanBoard.jsx
import { useEffect, useState } from "react";
import API from "../api/axios";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";

const columns = ["TODO", "IN_PROGRESS", "REVIEW", "DONE"];

export default function KanbanBoard() {
  const [tasks, setTasks] = useState({});

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    const res = await API.get("/tasks/kanban");
    setTasks(res.data);
  };

  const handleDragEnd = async (result) => {
    if (!result.destination) return;

    const taskId = result.draggableId;
    const newStatus = result.destination.droppableId;

    await API.patch(`/tasks/${taskId}/status`, {
      status: newStatus,
    });

    fetchTasks();
  };

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-4 gap-4 p-4">
        {columns.map((col) => (
          <Droppable droppableId={col} key={col}>
            {(provided) => (
              <div
                className="bg-gray-100 p-3 rounded-lg min-h-[400px]"
                ref={provided.innerRef}
                {...provided.droppableProps}
              >
                <h2 className="font-bold mb-3">{col}</h2>

                {tasks[col]?.map((task, index) => (
                  <Draggable
                    draggableId={String(task.id)}
                    index={index}
                    key={task.id}
                  >
                    {(provided) => (
                      <div
                        className="bg-white p-3 mb-2 rounded shadow"
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                      >
                        <p>{task.title}</p>
                      </div>
                    )}
                  </Draggable>
                ))}

                {provided.placeholder}
              </div>
            )}
          </Droppable>
        ))}
      </div>
    </DragDropContext>
  );
}