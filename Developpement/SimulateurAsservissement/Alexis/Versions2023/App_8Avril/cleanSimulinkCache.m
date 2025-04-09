function cleanSimulinkCache()
    % Manual cleanup of common Simulink cache and codegen folders

    % Define likely folders to remove
    foldersToDelete = {
        fullfile(tempdir, 'slprj')
        fullfile(tempdir, 'coder')
        fullfile(pwd, 'slprj')
        fullfile(pwd, 'coder')
        fullfile(pwd, 'work')
    };

    for k = 1:numel(foldersToDelete)
        folder = foldersToDelete{k};
        if isfolder(folder)
            try
                fprintf('🧹 Deleting folder: %s\n', folder);
                rmdir(folder, 's');
                fprintf('✅ Deleted: %s\n', folder);
            catch ME
                warning('⚠️ Could not delete folder "%s": %s', folder, ME.message);
            end
        else
            fprintf('ℹ️ Folder not found (already clean): %s\n', folder);
        end
    end

    % Also clear mex and cache
    fprintf('🧹 Cleaning MEX files and internal caches...\n');
    clear mex;
    rehash toolboxcache;
    fprintf('✅ MEX and toolbox cache cleared.\n');

    fprintf('🎉 Clean up done. Ready for fresh build!\n');
end
