-- CreateTable
CREATE TABLE "dp_history" (
    "id" SERIAL NOT NULL,
    "imageUrl" TEXT NOT NULL,
    "localPath" TEXT NOT NULL,
    "imageHash" TEXT NOT NULL,
    "capturedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "isChange" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "dp_history_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bot_state" (
    "id" INTEGER NOT NULL,
    "lastHash" TEXT,
    "lastCheckedAt" TIMESTAMP(3),

    CONSTRAINT "bot_state_pkey" PRIMARY KEY ("id")
);
