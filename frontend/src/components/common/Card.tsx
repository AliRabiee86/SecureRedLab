import { forwardRef, type HTMLAttributes } from 'react'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'bordered' | 'elevated'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ children, variant = 'default', padding = 'md', className = '', ...props }, ref) => {
    const baseStyles = 'glass-card overflow-hidden transition-all duration-500'

    const variants = {
      default: 'bg-white/5 border-white/10 hover:border-white/20',
      bordered: 'border-2 border-cyber-blue/20 bg-cyber-blue/5',
      elevated: 'shadow-[0_20px_50px_rgba(0,0,0,0.3)] bg-white/10',
    }

    const paddings = {
      none: '',
      sm: 'p-3',
      md: 'p-6',
      lg: 'p-8',
    }

    return (
      <div
        ref={ref}
        className={`${baseStyles} ${variants[variant]} ${paddings[padding]} ${className}`}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

export default Card
