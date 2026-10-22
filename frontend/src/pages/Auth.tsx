import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, Eye, EyeOff, FlaskConical, Lock, Mail, User } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ROUTES } from '@/lib/routes';
import { useSession } from '@/hooks/useSession';

const email = z.string().trim().min(1, 'Enter your email.').email('Enter a valid email address.');
const password = z.string().min(8, 'Use at least 8 characters.');
const loginSchema = z.object({ email, password: z.string().min(1, 'Enter your password.') });
const registerSchema = z.object({ name: z.string().trim().min(2, 'Enter your full name.'), email, password, confirm: z.string() })
  .refine((v) => v.password === v.confirm, { path: ['confirm'], message: 'Passwords do not match.' });
const recoverSchema = z.object({ email });

function Shell({ title, subtitle, children, footer }: { title: string; subtitle: string; children: React.ReactNode; footer: React.ReactNode }) {
  return (
    <div className="rp-ambient px-4 py-12 md:py-20">
      <Card className="mx-auto w-full max-w-[460px] !p-7 md:!p-9">
        <Badge tone="warning" className="mb-4"><FlaskConical className="h-3.5 w-3.5" aria-hidden /> Prototype: no auth backend connected</Badge>
        <h1 className="text-[30px] font-extrabold">{title}</h1>
        <p className="mt-1.5 text-sm text-rp-muted">{subtitle}</p>
        <div className="mt-6">{children}</div>
        <div className="mt-6 text-center text-sm text-rp-muted">{footer}</div>
      </Card>
    </div>
  );
}

function PasswordField({ label, error, reg }: { label: string; error?: string; reg: ReturnType<ReturnType<typeof useForm>['register']> }) {
  const [show, setShow] = useState(false);
  return (
    <Input
      label={label} type={show ? 'text' : 'password'} autoComplete="current-password" error={error} leading={<Lock className="h-4 w-4" />} {...reg}
      trailing={<button type="button" onClick={() => setShow((s) => !s)} aria-label={show ? 'Hide password' : 'Show password'} aria-pressed={show} className="grid h-9 w-9 place-items-center rounded-lg text-rp-muted hover:bg-rp-primary-light"><>{show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}</></button>}
    />
  );
}

const link = 'font-semibold text-rp-primary hover:text-rp-primary-hover';

export function Login() {
  const nav = useNavigate();
  const { signIn } = useSession();
  const f = useForm<z.infer<typeof loginSchema>>({ resolver: zodResolver(loginSchema) });
  const submit = f.handleSubmit(async (v) => {
    // No verified login endpoint exists yet. Start a device-local prototype session; the password is discarded.
    signIn({ name: v.email.split('@')[0], email: v.email });
    nav(ROUTES.dashboard);
  });
  return (
    <Shell title="Welcome back" subtitle="Log in to continue to your dashboard." footer={<>New to ReviewPulse? <Link className={link} to={ROUTES.register}>Create an account</Link></>}>
      <form onSubmit={submit} noValidate className="space-y-4">
        <Input label="Email" type="email" autoComplete="email" leading={<Mail className="h-4 w-4" />} error={f.formState.errors.email?.message} {...f.register('email')} />
        <PasswordField label="Password" error={f.formState.errors.password?.message} reg={f.register('password') as never} />
        <div className="flex justify-end text-sm"><Link className={link} to={ROUTES.recover}>Forgot password?</Link></div>
        <Button type="submit" size="lg" className="w-full" loading={f.formState.isSubmitting}>Log in</Button>
        <p className="text-xs text-rp-muted">Prototype mode starts a session on this device only. Credentials are not sent or stored.</p>
      </form>
    </Shell>
  );
}

export function Register() {
  const nav = useNavigate();
  const { signIn } = useSession();
  const f = useForm<z.infer<typeof registerSchema>>({ resolver: zodResolver(registerSchema) });
  const submit = f.handleSubmit((v) => { signIn({ name: v.name, email: v.email }); nav(ROUTES.dashboard); });
  const e = f.formState.errors;
  return (
    <Shell title="Create your account" subtitle="Start exploring product reviews." footer={<>Already registered? <Link className={link} to={ROUTES.login}>Log in</Link></>}>
      <form onSubmit={submit} noValidate className="space-y-4">
        <Input label="Full name" autoComplete="name" leading={<User className="h-4 w-4" />} error={e.name?.message} {...f.register('name')} />
        <Input label="Email" type="email" autoComplete="email" leading={<Mail className="h-4 w-4" />} error={e.email?.message} {...f.register('email')} />
        <PasswordField label="Password" error={e.password?.message} reg={f.register('password') as never} />
        <PasswordField label="Confirm password" error={e.confirm?.message} reg={f.register('confirm') as never} />
        <Button type="submit" size="lg" className="w-full" loading={f.formState.isSubmitting}>Create account</Button>
        <p className="text-xs text-rp-muted">No server account is created in prototype mode. This only starts a local session.</p>
      </form>
    </Shell>
  );
}

export function Recover() {
  const [done, setDone] = useState(false);
  const f = useForm<z.infer<typeof recoverSchema>>({ resolver: zodResolver(recoverSchema) });
  return (
    <Shell title="Reset your password" subtitle="Enter your email to request a reset link." footer={<Link className={`${link} inline-flex items-center gap-1`} to={ROUTES.login}><ArrowLeft className="h-4 w-4" aria-hidden />Back to log in</Link>}>
      <form onSubmit={f.handleSubmit(() => setDone(true))} noValidate className="space-y-4">
        <Input label="Email" type="email" autoComplete="email" leading={<Mail className="h-4 w-4" />} error={f.formState.errors.email?.message} {...f.register('email')} />
        <Button type="submit" size="lg" className="w-full">Request reset link</Button>
        {done && <p role="status" className="rounded-2xl border border-rp-warning/30 bg-rp-warning/15 p-3.5 text-sm text-rp-warning">Password recovery is not connected to a backend yet, so no email was sent.</p>}
      </form>
    </Shell>
  );
}
