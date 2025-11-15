// Initialisation MongoDB
db = db.getSiblingDB('appdb');

db.createCollection('notifications', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["type", "message", "created_at"],
            properties: {
                type: {
                    bsonType: "string", 
                    description: "must be a string and is required"
                },
                message: {
                    bsonType: "string",
                    description: "must be a string and is required"  
                },
                user_id: {
                    bsonType: "int", 
                    description: "must be an integer"
                },
                created_at: {
                    bsonType: "date",
                    description: "must be a date and is required"
                },
                status: {
                    bsonType: "string",
                    description: "must be a string"
                }
            }
        }
    }
});

db.createCollection('logs', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["level", "message", "timestamp"],
            properties: {
                level: {
                    bsonType: "string",  // Correction: "nbsonType" → "bsonType"
                    enum: ["info", "warning", "error"],
                    description: "must be a string and is required"
                },
                message: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                timestamp: {
                    bsonType: "date",
                    description: "must be a date and is required"
                },
                service: {
                    bsonType: "string",
                    description: "must be a string"
                }
            }
        }
    }
});

db.notifications.createIndex({"created_at": -1});
db.notifications.createIndex({"type": 1});
db.logs.createIndex({"timestamp": -1});
db.logs.createIndex({"level": 1}); 

print("MongoDB initialization completed");  