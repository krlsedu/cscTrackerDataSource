select gc.group_cost, round(saida / entradas, 6) as percentage, gc.ideal_value / 100 as ideal_value, saida, entradas
from (select *
      from (select cgc.group_cost, sum(t.value)
            from transactions t,
                 categories_group_costs cgc
            where t.category = cgc.category
              and t.type = 'outcome'
              and t.date >= :data_ini
              and t.date <= :data_fim
              and t.user_id = :user_id
            group by cgc.group_cost
            union
            select 'Outros', sum(d.value)
            from transactions d
            where not exists(select 1
                             from categories_group_costs cgc
                             where d.category = cgc.category
                                or d.category = cgc.group_cost)
              and type = 'outcome'
              and category <> 'Ignored'
              and date >= :data_ini
              and date <= :data_fim
              and d.user_id = :user_id
            union
            select 'Liberdade Financeira', (select coalesce (sum (quantity * usm_incres.price), 0)
                from user_stocks_movements usm_incres
                where usm_incres.user_id = :user_id
                and usm_incres.movement_type = 1
                and usm_incres.date >= :data_ini
                and usm_incres.date <= :data_fim) -
                (select coalesce (sum (quantity * usm_incres.price), 0)
                from user_stocks_movements usm_incres
                where usm_incres.user_id = :user_id
                and usm_incres.movement_type = 2
                and usm_incres.date >= :data_ini
                and usm_incres.date <= :data_fim)
            order by group_cost) as group_costs (group_cost, saida),
           (select 'Rendas', sum(income)
            from (select 'Rendas', sum(t.value)
                  from transactions t
                  where t.type = 'income'
                    and category <> 'Ignored'
                    and t.date >= :data_ini
                    and t.date <= :data_fim
                    and t.user_id = :user_id
                  union
                  select 'Rendas', sum(d.quantity * d.value_per_quote)
                  from dividends d
                  where d.date_payment >= :data_ini
                    and d.date_payment <= :data_fim
                    and d.user_id = :user_id
                  union
                  select 'Rendas', sum(p.quantity * p.value)
                  from profit_loss p
                  where p.user_id = :user_id
                    and p.date_sell >= :data_ini
                    and p.date_sell <= :data_fim) as group_incomes (group_income, income)) as group_incomes (group_income, entradas)) as t,
     group_costs gc
where t.group_cost = gc.group_cost
  and gc.user_id = :user_id
order by gc.group_cost;
