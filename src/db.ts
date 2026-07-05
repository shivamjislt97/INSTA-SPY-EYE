import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export default prisma;

export async function getBotState() {
  let state = await prisma.bot_state.findUnique({ where: { id: 1 } });
  if (!state) {
    state = await prisma.bot_state.create({
      data: { id: 1, lastHash: null, lastCheckedAt: null },
    });
  }
  return state;
}

export async function updateBotState(hash: string): Promise<void> {
  await prisma.bot_state.upsert({
    where: { id: 1 },
    update: { lastHash: hash, lastCheckedAt: new Date() },
    create: { id: 1, lastHash: hash, lastCheckedAt: new Date() },
  });
}

export async function insertDpHistory(entry: {
  imageUrl: string;
  localPath: string;
  imageHash: string;
  isChange: boolean;
}): Promise<void> {
  await prisma.dp_history.create({ data: entry });
}
