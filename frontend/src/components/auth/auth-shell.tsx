import Link from "next/link";
import { Leaf } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function AuthShell({
  title,
  description,
  children,
  footer,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-forest-950 px-6 py-12">
      <div className="w-full max-w-md">
        <Link href="/" className="mb-8 flex items-center justify-center gap-2">
          <Leaf className="h-7 w-7 text-leaf-400" />
          <span className="text-lg font-semibold">
            Natura<span className="text-leaf-400">AI</span>
          </span>
        </Link>
        <Card>
          <CardHeader>
            <CardTitle>{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </CardHeader>
          <CardContent>
            {children}
            {footer && <div className="mt-6 text-center text-sm">{footer}</div>}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
