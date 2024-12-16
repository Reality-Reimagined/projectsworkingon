-- Enable RLS (Row Level Security)
alter table if exists "public"."profiles" enable row level security;
alter table if exists "public"."conversions" enable row level security;
alter table if exists "public"."subscriptions" enable row level security;

-- Create profiles table
create table if not exists "public"."profiles" (
  "id" uuid references auth.users on delete cascade not null primary key,
  "email" text not null,
  "full_name" text,
  "avatar_url" text,
  "subscription_status" text default 'inactive',
  "subscription_tier" text default 'free',
  "created_at" timestamp with time zone default timezone('utc'::text, now()) not null,
  "updated_at" timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create conversions table for storing conversion history
create table if not exists "public"."conversions" (
  "id" uuid default uuid_generate_v4() primary key,
  "user_id" uuid references public.profiles(id) on delete cascade not null,
  "input_file_url" text not null,
  "output_file_url" text,
  "preview_url" text,
  "status" text default 'pending',
  "settings" jsonb default '{}',
  "created_at" timestamp with time zone default timezone('utc'::text, now()) not null,
  "updated_at" timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create subscriptions table
create table if not exists "public"."subscriptions" (
  "id" uuid default uuid_generate_v4() primary key,
  "user_id" uuid references public.profiles(id) on delete cascade not null,
  "stripe_customer_id" text,
  "stripe_subscription_id" text,
  "plan_id" text not null,
  "status" text default 'active',
  "current_period_end" timestamp with time zone,
  "cancel_at" timestamp with time zone,
  "created_at" timestamp with time zone default timezone('utc'::text, now()) not null,
  "updated_at" timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create RLS policies
create policy "Users can view own profile"
  on profiles for select
  using ( auth.uid() = id );

create policy "Users can update own profile"
  on profiles for update
  using ( auth.uid() = id );

create policy "Users can view own conversions"
  on conversions for select
  using ( auth.uid() = user_id );

create policy "Users can insert own conversions"
  on conversions for insert
  with check ( auth.uid() = user_id );

create policy "Users can view own subscriptions"
  on subscriptions for select
  using ( auth.uid() = user_id );

-- Create functions and triggers
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email);
  return new;
end;
$$ language plpgsql security definer;

-- Trigger for new user creation
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();