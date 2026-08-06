import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border",
  {
    variants: {
      variant: {
        default: "border-leaf-500/40 bg-forest-800 text-leaf-400",
        success: "border-leaf-500/50 bg-leaf-500/15 text-leaf-400",
        warning: "border-sun-500/50 bg-sun-500/15 text-sun-400",
        destructive: "border-terra-500/50 bg-terra-500/15 text-terra-500",
        outline: "border-forest-600 text-cream-200",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
