import { NextResponse } from "next/server";
import { saveManualEntry } from "../_shared";

export async function POST(request: Request) {
  try {
    await saveManualEntry("episode", await request.json());
    return NextResponse.json({ ok: true });
  } catch (error) {
    return NextResponse.json({ ok: false, error: String(error) }, { status: 500 });
  }
}
