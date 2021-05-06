function test_kinetics

dump_dir = '../fiberpy/fiberpy/package/modules/test/data/sim_output/hs';
n_bs = 3;
time_step = 0.001;

dump_files = sort_nat(findfiles('json', dump_dir, 0))';

bin_edges = linspace(-15, 15, 31);
possible = zeros(numel(bin_edges), 1, 2);
event = zeros(numel(bin_edges), 1, 2);


dump_ind = 100:199
dump_files = dump_files(dump_ind);

for fc = 1 : (numel(dump_files)-1)

    fc = fc
    
    if (fc==1)
        pre = loadjson(dump_files{fc});
        pre = tidy_structs(pre, n_bs);
        post  = loadjson(dump_files{fc+1});
        post = tidy_structs(post, n_bs);
    else
        pre = post;
        post = tidy_structs(loadjson(dump_files{fc+1}), n_bs);
    end

    for thick_i = 1 : numel(pre.thick)
        for cb_i = 1 : numel(pre.thick{thick_i}.cb_x)
            
            % Pull off m state
            m_state = pre.thick{thick_i}.cb_state(cb_i);
            
            m_parity = mod(cb_i, 2) + 1;
            
            if (m_state==1)
                % Head is detached
                m_x = pre.thick{thick_i}.cb_x(cb_i);
                
                a_f = pre.thick{thick_i}.cb_nearest_a_f(cb_i);
                
                % Cycle through binding sites
                for adj_i = 1 : n_bs
                    a_n = pre.thick{thick_i}.cb_nearest_a_n(adj_i, cb_i);
                    a_s = pre.thick{thick_i}.cb_nearest_a_n_states(adj_i, cb_i);
                    
                    if (a_s == 2)
                        % Site is on and available

                        a_x = pre.thin{a_f+1}.bs_x(a_n+1);
                        span_x = m_x - a_x;
                        bin_i = discretize(span_x, bin_edges);
                        if (~isnan(bin_i))
                            possible(bin_i, m_parity) =  ...
                                possible(bin_i, m_parity) + 1;
                        end

                        % Check whether cb is attached at end
%                         if ((pre.thin{a_f+1}.bound_to_m_f(a_n+1) == (thick_i-1)) && ...
%                                 (pre.thin{a_f+1}.bound_to_m_n(a_n+1) == (cb_i-1)))
%                         if ((pre.thin{a_f+1}.bound_to_m_f(a_n+1) == (thick_i-1)))
                        if ((pre.thin{a_f+1}.bound_to_m_n(a_n+1) == (cb_i-1)))
                            % Event happened
                            event(bin_i, m_parity) = event(bin_i, m_parity)+1;
                        end
                    end
                end
            end
        end
    end

    p = event./possible;
    for i = 1 : numel(bin_edges)
        for m = 1 : 2
            k(i,m) = -log(1-p(i,m)) / time_step;
        end
    end
    
    figure(1);
    cla;
    hold on;
    plot(bin_edges, k(:,1), 'r-');
    plot(bin_edges, k(:,2), 'g-');
    
    drawnow;
    
    if (fc==100)
        break
    end
end

end

% Sub functions

function s = tidy_structs(s, n_bs)

    for i = 1 : numel(s.thick)
        s.thick{i}.cb_nearest_a_n = zeros(n_bs, s.thick{i}.m_no_of_cbs);
        for j= 1:n_bs
            for k = 1 : 3
                if (k==1)
                    fs = sprintf('cb_nearest_a_n_0x5B_x_%i_0x5D_', j-1);
                    fs2 = 'cb_nearest_a_n';
                elseif (k==2)
                    fs = sprintf('cb_nearest_a_n_states_0x5B_x_%i_0x5D_', j-1);
                    fs2 = 'cb_nearest_a_n_states';
                elseif (k==3)
                    fs = sprintf('cb_nearest_bs_angle_diff_0x5B_x_%i_0x5D_', j-1);
                    fs2 = 'cb_nearest_bs_angle_diff';
                end
            
                s.thick{i}.(fs2)(j,:) = s.thick{i}.(fs);
                s.thick{i} = rmfield(s.thick{i}, fs);
            end
        end
    end
end