/- Lean 4 (mathlib 风格) 形式化目标陈述.
   本文件不依赖未发表引理; 全部定义自包含. 供后续形式化使用. -/

-- 座位安排: 一晚 = 桌的列表; 桌 = 人的循环序列
def Table := List ℕ
def Night := List Table
def Seating := List Night

/-- 人 x 与 y 在桌 T 上相邻 (循环意义下, 桌长 ≥ 2) -/
def adjacent (T : Table) (x y : ℕ) : Bool :=
  match T with
  | [] => false
  | [a] => false
  | _ => -- 循环邻接: y 是 x 在 T 中的循环前驱或后继
    let n := T.length
    (List.get? T ((T.indexOf x) + 1 % n)) = some y
    ∨ (List.get? T ((T.indexOf x) + n - 1 % n)) = some y

/-- 验证条件 (非正式公理化的计数谓词; 完整形式化需 Finmap 计数库支持) -/
-- 邻座次数 seatCount seat x y = ∑ 晚, ∑ 桌, 相邻次数

/-- 定理 T1 的目标陈述:
    对一切 n ≥ 4, 存在 HOP(2^⟨n-4⟩, 4, 4) 的解. -/
theorem T1_honeymoon_oberwolfach_44 :
    ∀ n : ℕ, 4 ≤ n →
    ∃ (S : Seating),
      -- (V1) 每晚每人恰坐一桌, 桌型 = 2 张 4 人桌 + (n-4) 张 2 人桌
      (∀ night ∈ S,
        (∀ p < 2*n, (night.flatMap id).count p = 1) ∧
        (night.map List.length).sorted = (List.replicate (n-4) 2 ++ [4, 4]).sorted) ∧
      -- (V3) 每晚每人与配偶邻座 (配偶 = xor 1)
      (∀ night ∈ S, ∀ p < 2*n,
        ∃ t ∈ night, adjacent t p (p ^ 1) ∨ adjacent t (p ^ 1) p) ∧
      -- (V4) 每个非配偶对恰邻座一次, 晚数 = n*(n-1)/2
      (S.length = n*(n-1)/2 ∧
        ∀ x y : ℕ, x < y → y < 2*n → x ≠ (y ^ 1) →
          (S.flatMap (fun night => night.flatMap (fun t => [if adjacent t x y ∨ adjacent t y x then 1 else 0])).sum = 1))

/-- 定理 T1' 的目标陈述: n 偶, t ∣ n/2, s = n - 2t ≥ 0 →
    HOP(2^⟨s⟩, 4^⟨t⟩) 有解 -/
theorem T1p_honeymoon_oberwolfach_uniform4 :
    ∀ n t : ℕ, 2 ∣ n → t ∣ n/2 → 2*t ≤ n →
    ∃ (S : Seating),
      (∀ night ∈ S,
        (∀ p < 2*n, (night.flatMap id).count p = 1) ∧
        (night.map List.length).sorted = (List.replicate (n - 2*t) 2 ++ List.replicate t 4).sorted) ∧
      (S.length = n*(n-1)/t ∧
        ∀ x y : ℕ, x < y → y < 2*n → x ≠ (y ^ 1) →
          (S.flatMap (fun night => night.flatMap (fun t => [if adjacent t x y ∨ adjacent t y x then 1 else 0])).sum = 1))

/- 构造骨架的形式化路线 (供后续工作):
   1. factorization (n) : Z_{n-1} ∪ {∞} 的轮换 1-factorization — 直接定义.
   2. 圈重组: 偶圈边序的 (e0,e2),(e1,e3),... 配对与 L ≡ 2 mod 4 的末 6 条特殊配对.
   3. 相位提升: 每标签对第 c 次出现取 α = c % 2, 桌序 [2u, 2u+1, 2v+α, 2v+1-α].
   4. 计数验证: 每非配偶对 = 标签对的 4 条人边, 两次出现 α 互补 → 各一次. -/
