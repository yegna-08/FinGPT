
import Link from "next/link";
export default function Navigation() {
  return (
    <nav className="w-full flex bg-purple-800 text-white">
      <div className="w-full flex justify-between items-center p-3 text-l text-foreground">
        <div className="flex items-center gap-4">
          <Link href="/" className="py-2 px-3 no-underline hover:underline">
            Home
          </Link>
          <Link href="/model-list" className="py-2 px-3 no-underline hover:underline">
            FinGPT Models
          </Link>
          <Link href="/inference" className="py-2 px-3 no-underline hover:underline">
            Inference
          </Link>
          <Link href="/faq" className="py-2 px-3 no-underline hover:underline">
            FAQ
          </Link>
        </div>
      </div>
    </nav>
  );
}
